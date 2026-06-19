import { Component, Input, OnChanges } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-risk-gauge',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="gauge-container">
      <svg viewBox="0 0 100 50" class="gauge">
        <!-- Background track -->
        <path class="gauge-bg" d="M 10 50 A 40 40 0 0 1 90 50" fill="none" stroke-width="10" stroke-linecap="round" />
        <!-- Score track -->
        <path class="gauge-value" [attr.stroke]="getColor()" [attr.stroke-dasharray]="dashArray" 
              d="M 10 50 A 40 40 0 0 1 90 50" fill="none" stroke-width="10" stroke-linecap="round" />
      </svg>
      <div class="score-display">
        <div class="score-value" [style.color]="getColor()">{{ score }}</div>
        <div class="score-label">{{ classificacao }}</div>
      </div>
    </div>
  `,
  styles: [`
    .gauge-container {
      position: relative;
      width: 200px;
      margin: 0 auto;
      text-align: center;
    }
    .gauge {
      width: 100%;
      height: 100px;
      overflow: visible;
    }
    .gauge-bg {
      stroke: var(--bg-tertiary);
    }
    .gauge-value {
      transition: stroke-dasharray 1s ease-out, stroke 0.5s ease;
    }
    .score-display {
      position: absolute;
      bottom: -10px;
      left: 0;
      width: 100%;
    }
    .score-value {
      font-size: 32px;
      font-weight: 800;
      line-height: 1;
    }
    .score-label {
      font-size: 14px;
      color: var(--text-secondary);
      text-transform: uppercase;
      font-weight: 600;
      margin-top: 4px;
    }
  `]
})
export class RiskGaugeComponent implements OnChanges {
  @Input() score: number = 0; // 0 to 100
  @Input() classificacao: string = 'N/A';

  dashArray: string = '0, 125.6'; // Math.PI * 40

  ngOnChanges() {
    const percentage = Math.max(0, Math.min(100, this.score)) / 100;
    const length = Math.PI * 40;
    const fill = percentage * length;
    const empty = length - fill;
    this.dashArray = `${fill}, ${empty}`;
  }

  getColor(): string {
    if (this.score >= 70) return 'var(--success)';
    if (this.score >= 40) return 'var(--warning)';
    return 'var(--danger)';
  }
}
