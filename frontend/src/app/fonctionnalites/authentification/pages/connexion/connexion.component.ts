import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../../../coeur/auth/auth.service';
import { InscriptionPayload } from '../../../../coeur/modeles/auth.model';

type ModeAuth = 'connexion' | 'inscription';

interface RoleOption {
  label: string;
  value: string;
}

@Component({
  selector: 'app-connexion',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './connexion.component.html',
  styleUrl: './connexion.component.scss',
})
export class ConnexionComponent {
  private readonly fb = inject(FormBuilder);
  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);

  readonly mode = signal<ModeAuth>('connexion');
  readonly chargement = signal(false);
  readonly erreur = signal('');
  readonly succes = signal('');

  readonly roles: RoleOption[] = [
    { label: 'Production Manager', value: 'PROD_MANAGER' },
    { label: 'Quality Manager', value: 'QUALITY_MANAGER' },
    { label: 'Repair Technician', value: 'REPAIR_TECHNICIAN' },
    { label: 'Test Manager', value: 'TEST_MANAGER' },
  ];

  readonly formulaireConnexion = this.fb.nonNullable.group({
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required]],
  });

  readonly formulaireInscription = this.fb.nonNullable.group({
    first_name: ['', [Validators.required, Validators.maxLength(150)]],
    last_name: ['', [Validators.required, Validators.maxLength(150)]],
    email: ['', [Validators.required, Validators.email]],
    matricule: ['', [Validators.required, Validators.maxLength(50)]],
    role: ['PROD_MANAGER'],
    password: ['', [Validators.required, Validators.minLength(8)]],
    confirm_password: ['', [Validators.required]],
  });

  basculerMode(mode: ModeAuth): void {
    this.mode.set(mode);
    this.erreur.set('');
    this.succes.set('');
  }

  soumettreConnexion(): void {
    if (this.formulaireConnexion.invalid) {
      this.formulaireConnexion.markAllAsTouched();
      return;
    }

    this.erreur.set('');
    this.succes.set('');
    this.chargement.set(true);

    this.authService.seConnecter(this.formulaireConnexion.getRawValue()).subscribe({
      next: () => {
        this.chargement.set(false);
        this.router.navigateByUrl('/');
      },
      error: (err) => {
        this.chargement.set(false);
        this.erreur.set(this.extraireErreur(err, 'Echec de connexion.'));
      },
    });
  }

  soumettreInscription(): void {
    if (this.formulaireInscription.invalid) {
      this.formulaireInscription.markAllAsTouched();
      return;
    }

    const raw = this.formulaireInscription.getRawValue();
    if (raw.password !== raw.confirm_password) {
      this.erreur.set('La confirmation du mot de passe ne correspond pas.');
      return;
    }

    this.erreur.set('');
    this.succes.set('');
    this.chargement.set(true);

    const payload: InscriptionPayload = {
      first_name: raw.first_name.trim(),
      last_name: raw.last_name.trim(),
      email: raw.email.trim().toLowerCase(),
      matricule: raw.matricule.trim().toUpperCase(),
      role: raw.role,
      password: raw.password,
      confirm_password: raw.confirm_password,
    };

    this.authService.inscrire(payload).subscribe({
      next: (res) => {
        this.chargement.set(false);
        this.succes.set(
          res?.message || 'Inscription effectuee. Verifiez votre email pour activer le compte.'
        );
        this.formulaireInscription.reset({
          first_name: '',
          last_name: '',
          email: '',
          matricule: '',
          role: 'PROD_MANAGER',
          password: '',
          confirm_password: '',
        });
        this.mode.set('connexion');
      },
      error: (err) => {
        this.chargement.set(false);
        this.erreur.set(this.extraireErreur(err, 'Echec de l inscription.'));
      },
    });
  }

  private extraireErreur(err: unknown, fallback: string): string {
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

    const detail = (payload as { detail?: string }).detail;
    if (detail) {
      return detail;
    }

    const message = (payload as { message?: string }).message;
    if (message) {
      return message;
    }

    return Object.entries(payload as Record<string, unknown>)
      .map(([key, value]) => {
        if (Array.isArray(value)) {
          return `${key}: ${value.join(', ')}`;
        }
        return `${key}: ${String(value)}`;
      })
      .join(' | ');
  }
}
