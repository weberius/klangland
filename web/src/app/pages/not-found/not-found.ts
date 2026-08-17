import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-not-found',
  imports: [RouterLink],
  template: `
    <section class="page-header">
      <h1>Seite nicht gefunden</h1>
      <p class="muted">Die angeforderte Seite existiert nicht.</p>
      <p><a class="btn btn-primary" routerLink="/">Zum Kalender</a></p>
    </section>
  `,
})
export class NotFoundPage {}
