import { CommonModule } from '@angular/common';
import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { forkJoin } from 'rxjs';
import { API_BASE_URL } from '../../../../coeur/constantes/api.const';
import {
  EtalonnageConformity,
  EtalonnageInstrument,
  EtalonnageInstrumentCreatePayload,
  EtalonnageRecord,
  EtalonnageRecordCreatePayload,
  EtalonnageState,
  EtalonnageTypeCode,
} from '../../../../coeur/modeles/etalonnage.model';
import { EtalonnageApi } from '../../../../coeur/services-api/etalonnage-api';

interface Option {
  label: string;
  value: string;
}

@Component({
  selector: 'app-accueil-etalonnage',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './accueil-etalonnage.html',
  styleUrl: './accueil-etalonnage.scss',
})
export class AccueilEtalonnage implements OnInit {
  private readonly fb = inject(FormBuilder);
  private readonly etalonnageApi = inject(EtalonnageApi);

  readonly typeOptions: Option[] = [
    { value: 'CHARGE', label: 'Charge' },
    { value: 'DIELECTRIC', label: 'Dielectric' },
    { value: 'GB_TESTER', label: 'GB TESTER' },
    { value: 'MESURE', label: 'Mesure' },
    { value: 'MULTIMETRE', label: 'Multimetre' },
    { value: 'OSCILL', label: 'Oscill' },
    { value: 'SWITCH', label: 'Switch' },
  ];

  readonly etatOptions: Option[] = [
    { value: 'GOOD', label: 'Bon' },
    { value: 'RESTRICTED', label: 'Utilisation avec restrictions' },
    { value: 'KO', label: 'KO' },
  ];

  readonly conformiteOptions: Option[] = [
    { value: 'CONFORM', label: 'Conforme' },
    { value: 'NON_CONFORM', label: 'Non conforme' },
  ];

  chargement = signal(true);
  enregistrementInstrument = signal(false);
  enregistrementRecord = signal(false);
  erreur = signal('');
  succes = signal('');

  instruments = signal<EtalonnageInstrument[]>([]);
  records = signal<EtalonnageRecord[]>([]);
  selectedPdfName = signal<string>('');
  selectedPdf = signal<File | null>(null);

  readonly instrumentsOptions = computed(() =>
    this.instruments().map((item) => ({
      id: item.id,
      label: `${item.instrument_code} - ${item.designation}`,
    }))
  );

  formulaireInstrument = this.fb.nonNullable.group({
    instrument_code: ['', [Validators.required, Validators.maxLength(100)]],
    designation: ['', [Validators.required, Validators.maxLength(255)]],
    type_code: ['MESURE' as EtalonnageTypeCode],
    sub_family_code: ['', [Validators.maxLength(100)]],
    serial_number: ['', [Validators.maxLength(150)]],
    brand: ['', [Validators.maxLength(150)]],
    affectation: ['', [Validators.maxLength(150)]],
    calibration_frequency_months: [12, [Validators.required, Validators.min(1)]],
    is_active: [true],
  });

  formulaireRecord = this.fb.nonNullable.group({
    instrument: [0, [Validators.required, Validators.min(1)]],
    calibration_date: [this.todayISO(), [Validators.required]],
    next_due_date: [this.todayISO(), [Validators.required]],
    calibration_state: ['GOOD' as EtalonnageState],
    result: ['CONFORM' as EtalonnageConformity],
    provider_name: ['', [Validators.maxLength(150)]],
    comment: [''],
  });

  ngOnInit(): void {
    this.chargerDonnees();
  }

  chargerDonnees(): void {
    this.chargement.set(true);
    this.erreur.set('');

    forkJoin({
      instruments: this.etalonnageApi.listerInstruments(),
      records: this.etalonnageApi.listerRecords(),
    }).subscribe({
      next: ({ instruments, records }) => {
        this.instruments.set(instruments);
        this.records.set(records);

        if (instruments.length > 0 && this.formulaireRecord.controls.instrument.value === 0) {
          this.formulaireRecord.patchValue({ instrument: instruments[0].id });
        }

        this.chargement.set(false);
      },
      error: () => {
        this.erreur.set('Impossible de charger les donnees etalonnage.');
        this.chargement.set(false);
      },
    });
  }

  onPdfSelection(event: Event): void {
    const input = event.target as HTMLInputElement | null;
    const file = input?.files?.[0];

    if (!file) {
      this.selectedPdf.set(null);
      this.selectedPdfName.set('');
      return;
    }

    this.selectedPdf.set(file);
    this.selectedPdfName.set(file.name);
  }

  soumettreInstrument(): void {
    if (this.formulaireInstrument.invalid) {
      this.formulaireInstrument.markAllAsTouched();
      return;
    }

    this.erreur.set('');
    this.succes.set('');
    this.enregistrementInstrument.set(true);

    const value = this.formulaireInstrument.getRawValue();
    const payload: EtalonnageInstrumentCreatePayload = {
      instrument_code: value.instrument_code.trim().toUpperCase(),
      designation: value.designation.trim(),
      type_code: value.type_code,
      sub_family_code: value.sub_family_code.trim().toUpperCase(),
      serial_number: value.serial_number.trim().toUpperCase(),
      brand: value.brand.trim(),
      affectation: value.affectation.trim().toUpperCase(),
      calibration_frequency_months: Number(value.calibration_frequency_months),
      is_active: value.is_active,
    };

    this.etalonnageApi.creerInstrument(payload).subscribe({
      next: (instrument) => {
        this.enregistrementInstrument.set(false);
        this.succes.set(`Instrument ${instrument.instrument_code} cree avec succes.`);
        this.formulaireInstrument.reset({
          instrument_code: '',
          designation: '',
          type_code: 'MESURE',
          sub_family_code: '',
          serial_number: '',
          brand: '',
          affectation: '',
          calibration_frequency_months: 12,
          is_active: true,
        });

        this.chargerDonnees();
      },
      error: (err) => {
        this.enregistrementInstrument.set(false);
        this.erreur.set(this.extraireErreurBackend(err));
      },
    });
  }

  soumettreRecord(): void {
    if (this.formulaireRecord.invalid) {
      this.formulaireRecord.markAllAsTouched();
      return;
    }

    this.erreur.set('');
    this.succes.set('');
    this.enregistrementRecord.set(true);

    const value = this.formulaireRecord.getRawValue();
    if (value.next_due_date < value.calibration_date) {
      this.erreur.set('La prochaine date prevue doit etre superieure ou egale a la date d etalonnage.');
      return;
    }

    const payload: EtalonnageRecordCreatePayload = {
      instrument: Number(value.instrument),
      calibration_date: value.calibration_date,
      next_due_date: value.next_due_date,
      calibration_state: value.calibration_state,
      result: value.result,
      provider_name: value.provider_name.trim(),
      comment: value.comment.trim(),
    };

    this.etalonnageApi.creerRecord(payload, this.selectedPdf()).subscribe({
      next: () => {
        this.enregistrementRecord.set(false);
        this.succes.set('Etalonnage enregistre avec succes.');
        this.formulaireRecord.reset({
          instrument: this.instruments().length > 0 ? this.instruments()[0].id : 0,
          calibration_date: this.todayISO(),
          next_due_date: this.todayISO(),
          calibration_state: 'GOOD',
          result: 'CONFORM',
          provider_name: '',
          comment: '',
        });
        this.selectedPdf.set(null);
        this.selectedPdfName.set('');
        this.chargerDonnees();
      },
      error: (err) => {
        this.enregistrementRecord.set(false);
        this.erreur.set(this.extraireErreurBackend(err));
      },
    });
  }

  libelleType(code: string): string {
    return this.typeOptions.find((item) => item.value === code)?.label || code;
  }

  libelleEtat(code: string): string {
    return this.etatOptions.find((item) => item.value === code)?.label || code;
  }

  libelleConformite(code: string): string {
    return this.conformiteOptions.find((item) => item.value === code)?.label || code;
  }

  instrumentLabel(id: number): string {
    const instrument = this.instruments().find((item) => item.id === id);
    return instrument ? `${instrument.instrument_code} - ${instrument.designation}` : `Instrument #${id}`;
  }

  reportUrl(path: string | null): string | null {
    if (!path) {
      return null;
    }

    if (path.startsWith('http://') || path.startsWith('https://')) {
      return path;
    }

    return `${new URL(API_BASE_URL).origin}${path}`;
  }

  private todayISO(): string {
    return new Date().toISOString().slice(0, 10);
  }

  private extraireErreurBackend(err: unknown): string {
    const fallback = 'Operation impossible.';
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
