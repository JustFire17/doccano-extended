<template>
  <v-card>
    <v-card-title class="text-h6">Annotations by Perspective</v-card-title>
    <v-card-text>
      <v-row>
        <v-col cols="12" md="6">
          <v-autocomplete
            v-model="selectedExamples"
            :items="examples"
            item-text="text"
            return-object
            label="Select examples"
            outlined
            multiple
            chips
            :loading="loading"
            @change="onExamplesChange"
          >
            <template #item="{ item }">
              <v-list-item-content>
                <v-list-item-title>{{ item.text }}</v-list-item-title>
              </v-list-item-content>
            </template>
          </v-autocomplete>
        </v-col>
        <v-col cols="12" md="6">
          <v-autocomplete
            v-model="selectedPerspectives"
            :items="perspectives"
            item-text="name"
            return-object
            label="Select perspectives"
            outlined
            multiple
            chips
            :loading="loadingPerspectives"
            @change="onPerspectivesChange"
          >
            <template #item="{ item }">
              <v-list-item-content>
                <v-list-item-title>{{ item.name }}</v-list-item-title>
                <v-list-item-subtitle>{{ item.type }}</v-list-item-subtitle>
              </v-list-item-content>
            </template>
          </v-autocomplete>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12" md="6">
          <v-autocomplete
            v-model="selectedValues"
            :items="perspectiveValues"
            :label="selectedPerspectives.length ? `Select values` : 'Select values'"
            outlined
            multiple
            chips
            :loading="loadingValues"
            :disabled="!selectedPerspectives.length"
            @change="onValuesChange"
          >
            <template #item="{ item }">
              <v-list-item-content>
                <v-list-item-title>{{ item }}</v-list-item-title>
              </v-list-item-content>
            </template>
          </v-autocomplete>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12" class="text-center">
          <v-btn
            color="primary"
            :loading="loadingSearch"
            :disabled="loadingSearch"
            @click="searchAnnotations"
          >
            Search
          </v-btn>
        </v-col>
      </v-row>
      <v-row v-if="errorMessage">
        <v-col cols="12" class="text-center">
          <v-alert
            type="error"
            dense
            text
          >
            {{ errorMessage }}
          </v-alert>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12">
          <v-data-table
            :headers="tableHeaders"
            :items="annotations"
            :items-per-page="10"
            class="elevation-1"
            :loading="loadingSearch"
            :sort-by="sortBy"
            :sort-desc="sortDesc"
            multi-sort
            @update:sort-by="sortBy = $event"
            @update:sort-desc="sortDesc = $event"
          >
            <template #item="{ item }">
              <tr>
                <td>
                  <div class="text-wrap">{{ item.example }}</div>
                </td>
                <td v-for="value in selectedValues" :key="value">
                  <div v-if="item.statistics[value] && item.statistics[value].length > 0" class="label-stats">
                    <div class="label-bars">
                      <div 
                        v-for="label in item.statistics[value]" 
                        :key="label.text"
                        class="label-bar"
                        :style="{
                          width: `${label.percentage}%`,
                          backgroundColor: label.backgroundColor
                        }"
                      >
                        {{ label.text }} ({{ Math.round(label.percentage) }}%)
                      </div>
                    </div>
                  </div>
                  <div v-else class="text-center grey--text">
                    No annotations
                  </div>
                </td>
              </tr>
            </template>
            <template #no-data>
              <div class="text-center pa-4">
                {{ loadingSearch ? 'Loading...' : (annotations.length === 0 ? 'No annotations' : 'No data available. Select filters and click Search.') }}
              </div>
            </template>
          </v-data-table>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script lang="ts">
import Vue from 'vue'
import { ExampleItem } from '~/domain/models/example/example'
import { PerspectiveDTO } from '~/services/application/perspective/perspectiveData'

interface Label {
  text: string
  backgroundColor: string
  count: number
  percentage: number
}

interface ExampleStatistics {
  example: string
  statistics: {
    [value: string]: Label[]
  }
}

export default Vue.extend({
  layout: 'project',

  middleware: ['check-auth', 'auth', 'setCurrentProject'],

  data() {
    return {
      examples: [] as ExampleItem[],
      selectedExamples: [] as ExampleItem[],
      perspectives: [] as PerspectiveDTO[],
      selectedPerspectives: [] as PerspectiveDTO[],
      selectedValues: [] as string[],
      perspectiveValues: [] as string[],
      loading: false,
      loadingPerspectives: false,
      loadingValues: false,
      loadingSearch: false,
      annotations: [] as ExampleStatistics[],
      errorMessage: '',
      sortBy: ['example'],
      sortDesc: [false],
      headers: [
        { text: 'Example', value: 'example', sortable: true, align: 'start' }
      ]
    }
  },

  async fetch() {
    await Promise.all([
      this.loadExamples(),
      this.loadPerspectives()
    ])
  },

  computed: {
    projectId() {
      return this.$route.params.id
    },
    tableHeaders() {
      const baseHeaders = [
        { text: 'Example', value: 'example', sortable: true, align: 'start' }
      ]
      
      // Add a column for each selected perspective value
      this.selectedValues.forEach(value => {
        baseHeaders.push({
          text: value,
          value,
          sortable: false,
          align: 'start'
        })
      })
      
      return baseHeaders
    }
  },

  methods: {
    async loadExamples() {
      this.loading = true
      try {
        const response = await this.$services.example.list(this.projectId, {
          limit: '100',
          offset: '0',
          q: '',
          isChecked: '',
          ordering: '-id'
        })
        this.examples = response.items
      } catch (error) {
        console.error('Error loading examples:', error)
      } finally {
        this.loading = false
      }
    },

    async loadPerspectives() {
      this.loadingPerspectives = true
      try {
        this.perspectives = await this.$services.perspective.list(this.projectId)
      } catch (error) {
        console.error('Error loading perspectives:', error)
      } finally {
        this.loadingPerspectives = false
      }
    },

    async loadPerspectiveValues() {
      if (!this.selectedPerspectives.length) return

      this.loadingValues = true
      this.selectedValues = []
      this.perspectiveValues = []

      try {
        const allValues = new Set<string>()
        
        for (const perspective of this.selectedPerspectives) {
          console.log('Processing Perspective:', perspective)
          console.log('Perspective Type:', perspective.type)
          console.log('Perspective Options:', perspective.options)

          if (perspective.type === 'yes/no') {
            allValues.add('Yes')
            allValues.add('No')
          } else if (perspective.options && perspective.options.trim() !== '') {
            // Para perspectivas com opções predefinidas
            const options = perspective.options.split(';').map(opt => opt.trim())
            options.forEach(opt => allValues.add(opt))
          } else if (perspective.type === 'string' || perspective.type === 'number') {
            // Para tipos string e number, precisamos buscar os valores preenchidos
            const filledValues = await this.$services.perspective.getAllFilledValues(this.projectId)
            const uniqueValues = filledValues[perspective.id] || []
            uniqueValues.forEach(val => allValues.add(val))
          }
        }

        this.perspectiveValues = Array.from(allValues)
        console.log('Final perspective values:', this.perspectiveValues)
      } catch (error) {
        console.error('Error loading perspective values:', error)
      } finally {
        this.loadingValues = false
      }
    },

    onExamplesChange() {
      // Will be implemented later
    },

    async onPerspectivesChange() {
      await this.loadPerspectiveValues()
    },

    onValuesChange() {
      // Will be implemented later
    },

    async searchAnnotations() {
      this.loadingSearch = true
      this.annotations = []
      this.errorMessage = ''

      try {
        let usersWithPerspective = []
        
        // If perspectives and values are selected, filter by those
        if (this.selectedPerspectives.length && this.selectedValues.length) {
          const allUsers = new Set<string>()
          
          for (const perspective of this.selectedPerspectives) {
            for (const value of this.selectedValues) {
              const users = await this.$services.perspective.getUsersWithValue(
                this.projectId,
                perspective.id,
                value
              )
              users.forEach(u => allUsers.add(u))
            }
          }
          
          usersWithPerspective = Array.from(allUsers)
        } else {
          // If no perspective filter, get all users
          const userResponse = await this.$repositories.user.list('')
          usersWithPerspective = userResponse.map(u => u.username)
        }

        console.log('Users to search:', usersWithPerspective)

        // Get examples if selected, otherwise get all examples
        let examples = []
        if (this.selectedExamples.length) {
          examples = this.selectedExamples
        } else {
          const response = await this.$services.example.list(this.projectId, {
            limit: '100',
            offset: '0',
            q: '',
            isChecked: '',
            ordering: '-id'
          })
          examples = response.items
        }

        const categoryTypes = await this.$services.categoryType.list(this.projectId)
        console.log('Category types:', categoryTypes)
        
        // Get annotations for each example and calculate statistics
        const annotations: ExampleStatistics[] = []
        for (const example of examples) {
          const exampleStats: ExampleStatistics = {
            example: example.text,
            statistics: {}
          }

          // Initialize statistics for each selected value
          this.selectedValues.forEach(value => {
            exampleStats.statistics[value] = []
          })

          // Get all annotations for this example
          const response = await this.$repositories.category.list(this.projectId, example.id)
          console.log('All annotations for example:', response)

          // Get all perspective values
          const allPerspectiveValues = await this.$services.perspective.getAllFilledValues(this.projectId)

          // Calculate statistics for each perspective value
          for (const value of this.selectedValues) {
            // Find which perspective this value belongs to
            const perspective = this.selectedPerspectives.find(p => {
              const values = allPerspectiveValues[p.id] || []
              return values.includes(value)
            })

            if (!perspective) continue

            // Get users who have this perspective value
            const usersWithValue = await this.$services.perspective.getUsersWithValue(
              this.projectId,
              perspective.id,
              value
            )

            // Filter annotations by users who have this perspective value
            const valueAnnotations = await this.filterAnnotationsByUsers(response, usersWithValue)

            // Count annotations by label
            const labelCounts = new Map<string, number>()
            valueAnnotations.forEach(annotation => {
              const categoryType = categoryTypes.find(ct => ct.id === annotation.label)
              if (categoryType) {
                const count = labelCounts.get(categoryType.text) || 0
                labelCounts.set(categoryType.text, count + 1)
              }
            })

            // Calculate percentages and create label objects
            const totalAnnotations = valueAnnotations.length
            const labels: Label[] = []
            labelCounts.forEach((count, text) => {
              const percentage = (count / totalAnnotations) * 100
              labels.push({
                text,
                backgroundColor: this.getRandomColor(text),
                count,
                percentage
              })
            })

            exampleStats.statistics[value] = labels
          }

          annotations.push(exampleStats)
        }

        this.annotations = annotations
        console.log('Final annotations:', annotations)
      } catch (error: any) {
        console.error('Error searching annotations:', error)
        if (error.response && error.response.status === 500) {
          this.errorMessage = 'Database unavailable. Please try again later.'
        } else {
          this.errorMessage = 'An error occurred while searching annotations.'
        }
      } finally {
        this.loadingSearch = false
      }
    },

    async filterAnnotationsByUsers(annotations: any[], usersWithValue: string[]) {
      const userResponse = await this.$repositories.user.list('')
      return annotations.filter(annotation => {
        const user = userResponse.find(u => u.id === annotation.user)
        return user !== undefined && usersWithValue.includes(user.username)
      })
    },

    getRandomColor(text: string): string {
      // Generate a consistent color based on the label text
      const colors = [
        '#2196F3', // Blue
        '#4CAF50', // Green
        '#FFC107', // Amber
        '#F44336', // Red
        '#9C27B0', // Purple
        '#FF9800', // Orange
        '#795548', // Brown
        '#607D8B', // Blue Grey
        '#E91E63', // Pink
        '#00BCD4'  // Cyan
      ]
      
      // Use the text to generate a consistent index
      const index = text.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0) % colors.length
      return colors[index]
    }
  }
})
</script>

<style scoped>
.label-stats {
  width: 100%;
}

.label-bars {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.label-bar {
  padding: 4px 8px;
  color: white;
  font-weight: bold;
  border-radius: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style> 