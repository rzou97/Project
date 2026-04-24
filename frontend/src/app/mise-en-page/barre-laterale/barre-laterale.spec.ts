import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BarreLaterale } from './barre-laterale.component';

describe('BarreLaterale', () => {
  let component: BarreLaterale;
  let fixture: ComponentFixture<BarreLaterale>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [BarreLaterale],
    }).compileComponents();

    fixture = TestBed.createComponent(BarreLaterale);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
