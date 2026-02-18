<template>
  <v-card>
    <v-card-text>
      <v-text-field
        v-model="search"
        label="Search"
        single-line
        hide-details
        filled
      />
      <v-data-table
        :headers="headers"
        :items="items"
        :items-per-page="10"
        :search="search"
        dense
        show-expand
        single-expand
        :expanded.sync="expanded"
        item-key="id"
        @click:row="handleRowClick"
        :custom-sort="customSort"
      >
        <template #no-data>
          <div class="text-center pa-4">
            No perspectives have been created yet. Create a perspective in a project to see it here.
          </div>
        </template>
        <template #[`item.associated_projects`]="{ item }">
          <span v-if="!item.associated_projects || item.associated_projects.length === 0" style="color: #bdbdbd;">No associated projects</span>
          <span v-else>
            <v-btn text color="primary" @click.stop="$emit('show-projects', item)">
              View more
            </v-btn>
          </span>
        </template>
        <template #[`item.created_at`]="{ item }">
          <span v-if="item.created_at">{{ formatDate(item.created_at) }}</span>
          <span v-else style="color: #bdbdbd;">-</span>
        </template>
        <template #[`item.updated_at`]="{ item }">
          <span v-if="item.updated_at">{{ formatDate(item.updated_at) }}</span>
          <span v-else style="color: #bdbdbd;">-</span>
        </template>
        <template #[`item.creator`]="{ item }">
          <span v-if="item.creator">{{ item.creator }}</span>
          <span v-else style="color: #bdbdbd;">-</span>
        </template>
        <template #expanded-item="{ headers, item }">
          <td :colspan="headers.length">
            <v-data-table
              :headers="itemHeaders"
              :items="item.items || []" 
              hide-default-footer
              dense
              class="expanded-table"
            >
              <template #[`item.type`]="{ item: typeItem }">
                {{ typeItem.type }}
              </template>
              <template #[`item.options`]="{ item: optionsItem }">
                {{ optionsItem.options || '-' }}
              </template>
            </v-data-table>
          </td>
        </template>
      </v-data-table>
    </v-card-text>
  </v-card>
</template>

<script lang="ts">
import Vue from 'vue'
import type { PropType } from 'vue'

interface PerspectiveItem {
  id: number
  name: string
  type: string
  options: string
}

interface Perspective {
  id: number
  name: string
  items: PerspectiveItem[]
  associated_projects: Array<{ id: number; name: string; version: string }>
  created_at: string
  updated_at: string
  creator: string
}

export default Vue.extend({
  props: {
    isLoading: {
      type: Boolean,
      default: false,
      required: true
    },
    items: {
      type: Array as PropType<Perspective[]>,
      default: () => [],
      required: true
    }
  },

  data() {
    return {
      search: '',
      expanded: [] as Perspective[]
    }
  },

  computed: {
    headers() {
      return [
        { text: 'Perspective Name', value: 'name', sortable: true },
        { text: 'Associated Projects', value: 'associated_projects', sortable: true },
        { text: 'Creation Date', value: 'created_at', sortable: true },
        { text: 'Last Modified', value: 'updated_at', sortable: true },
        { text: 'Creator', value: 'creator', sortable: true },
        { text: '', value: 'data-table-expand', sortable: false }
      ]
    },
    itemHeaders() {
      return [
        { text: 'Name', value: 'name', sortable: true },
        { text: 'Type', value: 'type', sortable: true },
        { text: 'Options', value: 'options', sortable: false }
      ]
    }
  },

  methods: {
    handleRowClick(item: Perspective) {
      const wasExpanded = this.expanded.some(expandedItem => expandedItem.id === item.id)
      this.expanded = wasExpanded ? [] : [item]
    },
    customSort(items: any[], sortBy: any[], sortDesc: boolean[]) {
      if (sortBy[0] === 'associated_projects') {
        return items.slice().sort((a: any, b: any) => {
          const aHas = a.associated_projects && a.associated_projects.length > 0 ? 1 : 0;
          const bHas = b.associated_projects && b.associated_projects.length > 0 ? 1 : 0;
          return sortDesc[0] ? bHas - aHas : aHas - bHas;
        });
      }
      // fallback para o sort padrão
      return items;
    },
    formatDate(dateStr: string) {
      const date = new Date(dateStr)
      return date.toLocaleDateString('pt-PT')
    }
  }
})
</script>

<style scoped>
.v-data-table {
  background: transparent !important;
}

.v-text-field {
  margin-bottom: 16px;
}

.expanded-table {
  margin: 8px 0;
  background: transparent !important;
}

::v-deep .v-data-table__expanded__content {
  box-shadow: none;
}
</style> 