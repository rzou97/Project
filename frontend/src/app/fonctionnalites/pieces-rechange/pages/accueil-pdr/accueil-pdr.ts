import { CommonModule } from '@angular/common';
import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { forkJoin } from 'rxjs';
import { Pdr, PdrCreatePayload, PdrStock } from '../../../../coeur/modeles/pdr.model';
import { PdrApi } from '../../../../coeur/services-api/pdr-api';

type VueCatalogue = 'cartes' | 'table';

interface AffectationOption {
  label: string;
  value: 'GENERAL' | 'TESTER' | 'INSTRUMENT';
}

@Component({
  selector: 'app-accueil-pdr',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './accueil-pdr.html',
  styleUrl: './accueil-pdr.scss',
})
export class AccueilPdr implements OnInit {
  private readonly fb = inject(FormBuilder);
  private readonly pdrApi = inject(PdrApi);

  readonly affectationTypes: AffectationOption[] = [
    { label: 'Generique', value: 'GENERAL' },
    { label: 'Tester', value: 'TESTER' },
    { label: 'Instruments', value: 'INSTRUMENT' },
  ];

  readonly vueCatalogue = signal<VueCatalogue>('cartes');
  readonly imageEnCours = signal<string | null>(null);
  readonly imagesLocales = signal<Record<string, string>>(this.chargerImagesLocales());

  chargement = signal(true);
  enregistrement = signal(false);
  erreur = signal('');
  succes = signal('');

  parts = signal<Pdr[]>([]);
  stocks = signal<PdrStock[]>([]);

  readonly stockByPartId = computed(() => {
    const map = new Map<number, PdrStock>();
    for (const stock of this.stocks()) {
      map.set(stock.part, stock);
    }
    return map;
  });

  readonly catalogueCartes = computed(() =>
    this.parts().map((part) => {
      const stock = this.stockByPartId().get(part.id);
      return {
        part,
        stockDisponible: stock?.available_quantity ?? 0,
        image:
          part.image_url ||
          this.imagesLocales()[part.part_code] ||
          'https://dummyimage.com/600x400/e5e7eb/374151&text=PDR',
      };
    })
  );

  formulairePart = this.fb.nonNullable.group({
    part_code: ['', [Validators.required, Validators.maxLength(100)]],
    designation: ['', [Validators.required, Validators.maxLength(255)]],
    manufacturer: ['', [Validators.maxLength(150)]],
    affectation_type: ['GENERAL' as 'GENERAL' | 'TESTER' | 'INSTRUMENT'],
    affectation_value: ['', [Validators.maxLength(150)]],
    minimum_stock: [0, [Validators.required, Validators.min(0)]],
    is_active: [true],
  });

  ngOnInit(): void {
    this.chargerDonnees();
  }

  chargerDonnees(): void {
    this.chargement.set(true);
    this.erreur.set('');

    forkJoin({
      parts: this.pdrApi.listerParts(),
      stocks: this.pdrApi.listerStocks(),
    }).subscribe({
      next: ({ parts, stocks }) => {
        this.parts.set(parts);
        this.stocks.set(stocks);
        this.chargement.set(false);
      },
      error: () => {
        this.erreur.set('Impossible de charger les donnees PDR.');
        this.chargement.set(false);
      },
    });
  }

  changerVue(vue: VueCatalogue): void {
    this.vueCatalogue.set(vue);
  }

  onImageSelection(event: Event): void {
    const input = event.target as HTMLInputElement | null;
    const fichier = input?.files?.[0];

    if (!fichier) {
      this.imageEnCours.set(null);
      return;
    }

    const reader = new FileReader();
    reader.onload = () => {
      this.imageEnCours.set(typeof reader.result === 'string' ? reader.result : null);
    };
    reader.readAsDataURL(fichier);
  }

  soumettrePart(): void {
    if (this.formulairePart.invalid) {
      this.formulairePart.markAllAsTouched();
      return;
    }

    this.erreur.set('');
    this.succes.set('');
    this.enregistrement.set(true);

    const valeur = this.formulairePart.getRawValue();
    const codePiece = valeur.part_code.trim().toUpperCase();
    const payload: PdrCreatePayload = {
      part_code: codePiece,
      designation: valeur.designation.trim(),
      manufacturer: valeur.manufacturer.trim(),
      affectation_type: valeur.affectation_type,
      affectation_value: valeur.affectation_value.trim().toUpperCase(),
      unit: 'PIECE',
      minimum_stock: Number(valeur.minimum_stock),
      is_active: valeur.is_active,
    };

    this.pdrApi.creerPart(payload).subscribe({
      next: () => {
        this.enregistrement.set(false);
        this.succes.set('Piece enregistree avec succes.');
        this.sauvegarderImageLocale(codePiece);
        this.formulairePart.reset({
          part_code: '',
          designation: '',
          manufacturer: '',
          affectation_type: 'GENERAL',
          affectation_value: '',
          minimum_stock: 0,
          is_active: true,
        });
        this.imageEnCours.set(null);
        this.chargerDonnees();
      },
      error: (err) => {
        this.enregistrement.set(false);
        this.erreur.set(this.extraireErreurBackend(err));
      },
    });
  }

  libelleAffectation(part: Pdr): string {
    const labels: Record<string, string> = {
      GENERAL: 'Generique',
      TESTER: 'Tester',
      INSTRUMENT: 'Instruments',
    };

    const type = labels[part.affectation_type] || part.affectation_type;
    return `${type}${part.affectation_value ? ` - ${part.affectation_value}` : ''}`;
  }

  libellePart(partId: number): string {
    const part = this.parts().find((item) => item.id === partId);
    if (!part) {
      return `Part #${partId}`;
    }

    return `${part.part_code} - ${part.designation}`;
  }

  private sauvegarderImageLocale(codePiece: string): void {
    const image = this.imageEnCours();
    if (!image) {
      return;
    }

    const nextImages = {
      ...this.imagesLocales(),
      [codePiece]: image,
    };
    this.imagesLocales.set(nextImages);
    localStorage.setItem('pdr_images_locales', JSON.stringify(nextImages));
  }

  private chargerImagesLocales(): Record<string, string> {
    const brut = localStorage.getItem('pdr_images_locales');
    if (!brut) {
      return {};
    }

    try {
      const parsed = JSON.parse(brut) as Record<string, string>;
      return parsed || {};
    } catch {
      return {};
    }
  }

  private extraireErreurBackend(err: unknown): string {
    const fallback = 'Echec lors de la creation de la piece.';
    const payload = (err as { error?: unknown })?.error;

    if (!payload) {
      return fallback;
    }

    if (typeof payload === 'string') {
      return payload;
    }

    if (typeof payload !== 'object') {
      return fallback;
    }

    const details = Object.entries(payload as Record<string, unknown>)
      .map(([champ, valeur]) => {
        if (Array.isArray(valeur)) {
          return `${champ}: ${valeur.join(', ')}`;
        }
        return `${champ}: ${String(valeur)}`;
      })
      .join(' | ');

    return details || fallback;
  }
}
