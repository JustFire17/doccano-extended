<template>
    <v-dialog v-model="dialog" max-width="800px">
      <v-card>
        <v-card-title class="text-h6">
          Report Discrepancy
        </v-card-title>
  
        <v-card-text>
          <p v-if="example"><strong>Text:</strong></p>
          <div v-if="example" class="dataset-text-container">
            <div style="white-space: pre-wrap;">{{ example.text }}</div>
          </div>
          <p v-else>No example selected</p>
  
          <div v-if="labelStats.length">
            <p><strong>Labels:</strong></p>
            <v-list dense>
              <v-list-item v-for="(label, index) in labelStats" :key="index">
                <v-list-item-content>
                  <v-chip
                    :color="getColor(label.percentage)"
                    class="ma-1"
                    small
                  >
                    {{ label.label_text }}
                  </v-chip>
                  <span>Used {{ label.vote_count }}x – {{ label.percentage.toFixed(1) }}%</span>
                </v-list-item-content>
              </v-list-item>
            </v-list>
          </div>
          <v-alert
            v-else
            type="warning"
            dense
            text
          >
            No labels found for this example. Please add labels before reporting a discrepancy.
          </v-alert>
        </v-card-text>
  
        <v-card-actions>
          <v-spacer />
          <v-btn text @click="close">Cancel</v-btn>
          <v-btn 
            color="primary" 
            :disabled="!isValid" 
            :loading="isSubmitting"
            @click="submit"
          >
            Report Discrepancy
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </template>
  
  <script lang="ts">
  import Vue from 'vue'
  import { ExampleDTO } from '~/services/application/example/exampleData'
  
  export default Vue.extend({
    props: {
      value: {
        type: Boolean,
        required: true
      },
      example: {
        type: Object as () => ExampleDTO,
        required: false,
        default: null
      }
    },
  
    data() {
      return {
        labelStats: [] as { label_text: string; vote_count: number; percentage: number }[],
        isSubmitting: false,
        internalDialog: false
      }
    },
  
    computed: {
      dialog: {
        get(): boolean {
          return this.internalDialog
        },
        set(val: boolean) {
          if (val) {
            this.checkAndOpenDialog()
          } else {
            this.internalDialog = false
            this.$emit('input', false)
          }
        }
      },
  
      isValid(): boolean {
        return this.labelStats.length > 0
      }
    },
  
    watch: {
      value: {
        immediate: true,
        handler(val: boolean) {
          if (val) {
            this.checkAndOpenDialog()
          } else {
            this.internalDialog = false
          }
        }
      },
      
      example: {
        immediate: true,
        async handler(newExample) {
          if (!newExample) return
          const projectId = this.$route.params.id

          // Buscar estatísticas das labels
          try {
            const stats = await this.$services.discrepancy.getLabelStats(projectId, newExample.id)
            const total = Object.values(stats).reduce((acc, val) => acc + val.count, 0)
            this.labelStats = Object.entries(stats).map(([labelText, data]: any) => ({
              label_text: labelText,
              vote_count: data.count,
              percentage: total > 0 ? (data.count / total) * 100 : 0
            }))
          } catch (error) {
            console.error('Error fetching label stats:', error)
            this.labelStats = []
          }
        }
      }
    },
  
    methods: {
      checkAndOpenDialog() {
        if (!this.example) {
          this.internalDialog = false
          this.$emit('input', false)
          return
        }

        this.internalDialog = true
        this.$emit('input', true)
      },
  
      close() {
        this.dialog = false
        this.labelStats = []
      },
  
      async submit() {
        if (!this.isValid) {
          return
        }
  
        this.isSubmitting = true
        try {
          const projectId = Number(this.$route.params.id)
          const labelStats = this.labelStats.map(label => ({
            label_text: label.label_text,
            vote_count: label.vote_count,
            percentage: label.percentage
          }))
  
          await this.$services.manualDiscrepancy.submit(projectId, {
            example: this.example.id,
            description: '',
            label_stats: labelStats
          })
  
          alert('Discrepancy reported successfully!')
          this.close()
        } catch (error: any) {
          if (error.response) {
            if (error.response.status === 500) {
              alert('Database unavailable, please try again later.')
            } else if (error.response.data) {
              const errors = error.response.data
              if (errors.error) {
                alert(errors.error)
              } else if (errors.example) {
                alert(errors.example[0])
              } else if (errors.label_stats) {
                alert(errors.label_stats[0])
              } else {
                alert('An unexpected error occurred.')
              }
            }
          } else {
            alert('Failed to connect to the server.')
          }
          console.error('Failed to submit discrepancy:', error)
        } finally {
          this.isSubmitting = false
        }
      },
  
      getColor(percentage: number): string {
        if (percentage >= 80) return 'success'
        if (percentage >= 50) return 'warning'
        return 'error'
      }
    }
  })
  </script>

<style scoped>
.dataset-text-container {
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  padding: 12px;
  margin-bottom: 16px;
  background-color: #f5f5f5;
}

.dataset-text-container::-webkit-scrollbar {
  width: 8px;
}

.dataset-text-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.dataset-text-container::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

.dataset-text-container::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style>