import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    pathMatch: 'full',
    loadComponent: () => import('./pages/calendar/calendar').then((m) => m.CalendarPage),
    title: 'Kalender · Klangland',
  },
  {
    path: 'calendar/:year/:month',
    loadComponent: () => import('./pages/calendar/calendar').then((m) => m.CalendarPage),
    title: 'Kalender · Klangland',
  },
  {
    path: 'ensembles',
    loadComponent: () => import('./pages/ensemble-list/ensemble-list').then((m) => m.EnsembleListPage),
    title: 'Ensembles · Klangland',
  },
  {
    path: 'ensembles/:id',
    loadComponent: () => import('./pages/ensemble-detail/ensemble-detail').then((m) => m.EnsembleDetailPage),
    title: 'Ensemble · Klangland',
  },
  {
    path: 'venues',
    loadComponent: () => import('./pages/venue-list/venue-list').then((m) => m.VenueListPage),
    title: 'Spielstätten · Klangland',
  },
  {
    path: 'venues/:id',
    loadComponent: () => import('./pages/venue-detail/venue-detail').then((m) => m.VenueDetailPage),
    title: 'Spielstätte · Klangland',
  },
  {
    path: 'events/:id',
    loadComponent: () => import('./pages/event-detail/event-detail').then((m) => m.EventDetailPage),
    title: 'Veranstaltung · Klangland',
  },
  {
    path: '**',
    loadComponent: () => import('./pages/not-found/not-found').then((m) => m.NotFoundPage),
    title: 'Nicht gefunden · Klangland',
  },
];
