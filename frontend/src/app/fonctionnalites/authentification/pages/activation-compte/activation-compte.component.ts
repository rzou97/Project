import { CommonModule } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { AuthService } from '../../../../coeur/auth/auth.service';
import { ROUTE_PATHS } from '../../../../coeur/constantes/routes.const';

@Component({
  selector: 'app-activation-compte',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './activation-compte.component.html',
  styleUrl: './activation-compte.component.scss',
})
export class ActivationCompteComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly authService = inject(AuthService);

  chargement = signal(true);
  succes = signal(false);
  message = signal('Activation du compte en cours...');

  readonly routeConnexion = `/${ROUTE_PATHS.connexion}`;

  ngOnInit(): void {
    const uidb64 = this.route.snapshot.paramMap.get('uidb64');
    const token = this.route.snapshot.paramMap.get('token');

    if (!uidb64 || !token) {
      this.chargement.set(false);
      this.succes.set(false);
      this.message.set('Lien d activation invalide.');
      return;
    }

    this.authService.activerCompte(uidb64, token).subscribe({
      next: (res) => {
        this.chargement.set(false);
        this.succes.set(true);
        this.message.set(res?.message || 'Compte active avec succes. Vous pouvez vous connecter.');
      },
      error: (err) => {
        this.chargement.set(false);
        this.succes.set(false);
        this.message.set(err?.error?.message || 'Lien d activation invalide ou expire.');
      },
    });
  }
}
