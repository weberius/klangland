import { Component, computed, inject } from '@angular/core';
import { RouterLink } from '@angular/router';

import { DataService } from '../../core/data.service';
import { FilterService } from '../../core/filter.service';
import { Composer, Work } from '../../models/models';
import { PageHeader } from '../../shared/page-header/page-header';

interface ComposerCardView {
  composer: Composer;
  life: string;
  portraitUrl: string | null;
  works: Work[];
  moreWorksCount: number;
}

@Component({
  selector: 'app-composer-list',
  imports: [RouterLink, PageHeader],
  templateUrl: './composer-list.html',
  styleUrl: './composer-list.css',
})
export class ComposerListPage {
  private data = inject(DataService);
  private filter = inject(FilterService);

  readonly loading = computed(() => this.data.loading());

  /**
   * Kachel-Modell des Komponist:innen-Grids. Ermittelt die programmierten Werke
   * genau EINMAL über {@link DataService.worksForFilter} (O(Events)) und gruppiert
   * sie lokal nach Komponist:in. Früher wurde worksForFilter pro Komponist:in erneut
   * ausgeführt (1 + n Aufrufe, jeweils inkl. localeCompare-Sortierung) – das führte
   * auf schwachen Geräten zu ~2 s Hauptthread-Blockade beim Öffnen der Seite.
   */
  readonly cards = computed<ComposerCardView[]>(() => {
    const cityIds = this.filter.selectedCityIds();
    const profileIds = this.filter.selectedProfileIds();

    // worksForFilter liefert bereits nach Komponist:in-Name und dann Werktitel
    // sortiert – die Gruppierung erhält damit je Komponist:in die Titel-Reihenfolge.
    const byComposer = new Map<string, Work[]>();
    for (const work of this.data.worksForFilter(cityIds, profileIds)) {
      const list = byComposer.get(work.composerId);
      if (list) list.push(work);
      else byComposer.set(work.composerId, [work]);
    }

    return [...byComposer.keys()]
      .map((id) => this.data.composer(id))
      .filter((c): c is Composer => Boolean(c))
      .sort((a, b) => a.name.localeCompare(b.name, 'de'))
      .map((composer) => {
        const works = byComposer.get(composer.id) ?? [];
        const preview = works.slice(0, 3);
        return {
          composer,
          life: this.life(composer),
          portraitUrl: this.portraitUrl(composer),
          works: preview,
          moreWorksCount: Math.max(0, works.length - preview.length),
        };
      });
  });

  life(c: Composer): string {
    const l = c.life;
    if (!l || l.from === null) return '';
    return l.to ? `${l.from}–${l.to}` : `* ${l.from}`;
  }

  portraitUrl(c: Composer): string | null {
    return c.portrait ? `portraits/${c.portrait.file}` : null;
  }
}
