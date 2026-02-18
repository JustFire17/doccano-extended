<template>
    <v-container class="pt-10" fluid>
      <v-card>
        <v-card-title class="text-h5">
          Discrepancies
        </v-card-title>
        <v-card-text>
          <v-data-table
            :headers="headers"
            :items="items"
            :loading="isLoading"
            :loading-text="$t('generic.loading')"
            :no-data-text="'No items found.'"
            item-key="id"
            class="elevation-1"
          >
            <template #[`item.example_text`]="{ item }">
              <div class="dataset-text-container">
                <div style="white-space: pre-wrap;">{{ item.example_text || `Loading example #${item.example}...` }}</div>
              </div>
            </template>

            <template #[`item.label_stats`]="{ item }">
              <div>
                <v-chip
                  v-for="stat in item.label_stats"
                  :key="stat.label_text"
                  :color="getColor(stat.percentage)"
                  class="ma-1"
                  small
                >
                  {{ stat.label_text }} ({{ stat.percentage.toFixed(1) }}%)
                </v-chip>
              </div>
            </template>

            <template #[`item.created_at`]="{ item }">
              {{ formatDate(item.created_at) }}
            </template>
  
            <template #[`item.reported_by_username`]="{ item }">
              {{ item.reported_by_username }}
            </template>

            <template #[`item.comments`]="{ item }">
              <v-btn small color="primary" @click="openComments(item.id)">Comments</v-btn>
            </template>
          </v-data-table>
          <v-dialog v-model="showCommentsModal" max-width="600px">
            <v-card>
              <v-card-title>
                Discrepancy Comments
                <v-spacer />
                <v-btn icon @click="showCommentsModal = false"><v-icon>mdi-close</v-icon></v-btn>
              </v-card-title>
              <v-card-text>
                <DiscrepancyComments v-if="selectedDiscrepancyId" :discrepancyId="selectedDiscrepancyId" />
              </v-card-text>
            </v-card>
          </v-dialog>
        </v-card-text>
      </v-card>
    </v-container>
  </template>
  
  <script lang="ts">
  import Vue from 'vue'
  import DiscrepancyComments from '@/components/discrepancies/DiscrepancyComments.vue'

  interface LabelStat {
    label_text: string
    vote_count: number
    percentage: number
  }

  interface MemberRole {
    isProjectAdmin: boolean
    isAnnotationApprover: boolean
  }

  interface ManualDiscrepancy {
    id: number
    project: number
    example: number
    reported_by: number | null
    reported_by_username: string | null
    description: string
    status: string
    created_at: string
    updated_at: string
    label_stats: LabelStat[]
  }

  interface TableItem extends ManualDiscrepancy {
    labels: LabelStat[]
    example_text?: string
  }
  
  export default Vue.extend({
    layout: 'project',
  
    middleware: ['check-auth', 'auth'],

    validate({ app, params }) {
      return app.$repositories.member.fetchMyRole(params.id).then((member: MemberRole) => {
        return member.isProjectAdmin || member.isAnnotationApprover
      })
    },

    data() {
      return {
        isLoading: false,
        items: [] as TableItem[],
        headers: [
          { 
            text: 'Dataset Text',
            value: 'example_text',
            width: '40%'
          },
          { 
            text: 'Labels',
            value: 'label_stats',
            width: '25%'
          },
          { 
            text: 'Reported by',
            value: 'reported_by_username',
            width: '20%'
          },
          { 
            text: 'Reported date',
            value: 'created_at',
            width: '15%'
          },
          { text: 'Comments', value: 'comments', width: '10%' }
        ],
        showCommentsModal: false,
        selectedDiscrepancyId: null as number | null
      }
    },
  
    async fetch() {
      this.isLoading = true
      try {
        const discrepancies = await this.service.list(this.projectId)
        console.log('Raw discrepancies:', discrepancies)
        
        // Primeiro, mapear os dados básicos
        this.items = discrepancies.map((item: ManualDiscrepancy): TableItem => ({
          ...item,
          labels: item.label_stats,
          example_text: ''
        }))

        // Depois, buscar o texto de cada exemplo
        await Promise.all(
          this.items.map(async (item) => {
            try {
              const example = await this.$services.example.findById(this.projectId, item.example)
              item.example_text = example.text
            } catch (e) {
              console.error(`Error loading example ${item.example}:`, e)
              item.example_text = `Error loading example #${item.example}`
            }
          })
        )
      } catch (e) {
        console.error('Error loading discrepancies:', e)
      } finally {
        this.isLoading = false
      }
    },
  
    computed: {
      projectId(): string {
        return this.$route.params.id
      },
  
      service(): any {
        return this.$services.manualDiscrepancy
      }
    },
  
    methods: {
      getColor(percentage: number): string {
        if (percentage >= 80) return 'success'
        if (percentage >= 50) return 'warning'
        return 'error'
      },

      formatDate(dateString: string): string {
        if (!dateString) return ''
        const date = new Date(dateString)
        return date.toLocaleDateString('pt-BR', {
          day: '2-digit',
          month: '2-digit',
          year: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        })
      },

      openComments(id: number) {
        this.selectedDiscrepancyId = id;
        this.showCommentsModal = true;
      }
    },
    components: {
      DiscrepancyComments
    }
  })
</script>

<style scoped>
.dataset-text-container {
  max-height: 150px;
  overflow-y: auto;
  border: none;
  padding: 4px;
}

.dataset-text-container::-webkit-scrollbar {
  width: 6px;
}

.dataset-text-container::-webkit-scrollbar-track {
  background: transparent;
}

.dataset-text-container::-webkit-scrollbar-thumb {
  background: #ddd;
  border-radius: 4px;
}

.dataset-text-container::-webkit-scrollbar-thumb:hover {
  background: #ccc;
}

.v-data-table {
  width: 100%;
}

.text-subtitle-2 {
  font-weight: 500;
}

.v-chip {
  font-weight: 500;
}

.v-chip.v-size--small {
  height: 24px;
}

.v-data-table ::v-deep tbody tr {
  cursor: default;
}

.v-data-table ::v-deep .v-data-table__wrapper {
  overflow-x: auto;
}
</style> 