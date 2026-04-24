import { CommonModule } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { forkJoin } from 'rxjs';
import {
  RepairPrediction,
  RepairProcedureTemplate,
} from '../../../../coeur/modeles/action-reparation.model';
import { AgentPredictionApi } from '../../../../coeur/services-api/agent-prediction-api';

@Component({
  selector: 'app-accueil-agent-prediction',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './accueil-agent-prediction.html',
  styleUrl: './accueil-agent-prediction.scss',
})
export class AccueilAgentPrediction implements OnInit {
  private readonly agentPredictionApi = inject(AgentPredictionApi);

  chargement = signal(true);
  erreur = signal('');
  predictions = signal<RepairPrediction[]>([]);
  procedures = signal<RepairProcedureTemplate[]>([]);

  ngOnInit(): void {
    this.chargerDonnees();
  }

  chargerDonnees(): void {
    this.chargement.set(true);
    this.erreur.set('');

    forkJoin({
      predictions: this.agentPredictionApi.listerPredictions(),
      procedures: this.agentPredictionApi.listerProcedures(),
    }).subscribe({
      next: ({ predictions, procedures }) => {
        this.predictions.set(predictions);
        this.procedures.set(procedures);
        this.chargement.set(false);
      },
      error: () => {
        this.erreur.set('Impossible de charger les donnees IA.');
        this.chargement.set(false);
      },
    });
  }
}
