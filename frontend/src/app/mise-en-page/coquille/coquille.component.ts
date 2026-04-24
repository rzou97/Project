import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet } from '@angular/router';
import { BarreLateraleComponent } from '../barre-laterale/barre-laterale.component'
import { EnTeteComponent } from '../en-tete/en-tete.component';
@Component({
  selector: 'app-coquille',
  standalone: true,
  imports: [CommonModule, RouterOutlet, BarreLateraleComponent, EnTeteComponent],
  templateUrl: './coquille.component.html',
  styleUrl: './coquille.component.scss',
})
export class CoquilleComponent {}