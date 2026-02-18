<template>
  <v-container>
    <v-card>
      <v-card-title class="text-h5">
        Side-by-Side Annotations
      </v-card-title>
      <v-card-text>
        <v-alert v-if="isLoading" type="info" border="left" prominent>
          Loading annotations, please wait...
        </v-alert>
        <v-alert v-if="error" type="error" border="left" prominent>
          {{ error }}
        </v-alert>

        <v-row>
          <v-col cols="12" md="6">
            <v-select
              v-model="selectedUsers"
              :items="users"
              label="Select Users to Display"
              multiple
              chips
              class="mb-4"
              :menu-props="{ maxHeight: '400px' }"
            >
              <template #selection="{ item, index }">
                <v-chip
                  v-if="index < 3"
                  :key="item"
                  close
                  @click:close="removeUser(item)"
                >
                  {{ item }}
                </v-chip>
                <span v-if="index === 3" class="grey--text text-caption">
                  (+{{ selectedUsers.length - 3 }} others)
                </span>
              </template>
            </v-select>
          </v-col>
          <v-col cols="12" md="6">
            <v-select
              v-model="selectedExamples"
              :items="examples"
              item-text="text"
              return-object
              label="Select Examples to Display"
              multiple
              chips
              class="mb-4"
              :menu-props="{ maxHeight: '400px' }"
            >
              <template #selection="{ item, index }">
                <v-chip
                  v-if="index < 3"
                  :key="item.id"
                  close
                  @click:close="removeExample(item)"
                >
                  {{ item.text.length > 50 ? item.text.substring(0, 50) + '...' : item.text }}
                </v-chip>
                <span v-if="index === 3" class="grey--text text-caption">
                  (+{{ selectedExamples.length - 3 }} others)
                </span>
              </template>
            </v-select>
          </v-col>
        </v-row>

        <v-row>
          <v-col cols="12">
            <v-switch
              v-model="showOnlyDiscrepancies"
              label="Show only examples with manual discrepancies"
              color="error"
              class="mb-4"
            ></v-switch>
          </v-col>
        </v-row>

        <div class="table-container">
          <v-data-table
            :headers="tableHeaders"
            :items="filteredAnnotations"
            :loading="isLoading"
            :items-per-page="10"
            class="elevation-1"
            fixed-header
            height="400px"
            :sort-by="sortBy"
            :sort-desc="sortDesc"
            @update:sort-by="onSortByUpdate"
            @update:sort-desc="onSortDescUpdate"
          >
            <template #[`item.text`]="{ item }">
              <div class="example-cell">
                <span class="d-flex d-sm-none">{{ item.text.length > 50 ? item.text.substring(0, 50) + '...' : item.text }}</span>
                <span class="d-none d-sm-flex">{{ item.text.length > 200 ? item.text.substring(0, 200) + '...' : item.text }}</span>
              </div>
            </template>
            <template #[`item.label_percentages`]="{ item }">
              <div>
                <v-chip
                  v-for="(percentage, label) in getLabelPercentages(item)"
                  :key="label"
                  :color="getColor(percentage)"
                  class="ma-1"
                  small
                >
                  {{ label }} ({{ percentage.toFixed(1) }}%)
                </v-chip>
              </div>
            </template>
            <template #item="{ item }">
              <tr :class="{ 'discrepancy-row': hasDiscrepancy(item.id) }">
                <td>
                  <div class="example-cell">
                    <span class="d-flex d-sm-none">{{ item.text.length > 50 ? item.text.substring(0, 50) + '...' : item.text }}</span>
                    <span class="d-none d-sm-flex">{{ item.text.length > 200 ? item.text.substring(0, 200) + '...' : item.text }}</span>
                  </div>
                </td>
                <td v-for="user in selectedUsers" :key="user">
                  {{ item.annotations[user] || 'No annotations' }}
                </td>
                <td>
                  <div>
                    <v-chip
                      v-for="(percentage, label) in getLabelPercentages(item)"
                      :key="label"
                      :color="getColor(percentage)"
                      class="ma-1"
                      small
                    >
                      {{ label }} ({{ percentage.toFixed(1) }}%)
                    </v-chip>
                  </div>
                </td>
              </tr>
            </template>
          </v-data-table>
        </div>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import axios from 'axios'
import Vue from 'vue'
import { ExampleItem } from '~/domain/models/example/example'

interface ExampleWithAnnotations {
  id: number;
  text: string;
  annotations: Record<string, string>;
  labelPercentages: Record<string, number>;
}

interface CategoryType {
  id: number
  text: string
}

interface ComponentData {
  isLoading: boolean;
  error: string | null;
  examples: ExampleItem[];
  selectedExamples: ExampleItem[];
  users: string[];
  selectedUsers: string[];
  categoryTypes: CategoryType[];
  annotations: ExampleWithAnnotations[];
  sortBy: string[];
  sortDesc: boolean[];
  manualDiscrepancies: number[];
  showOnlyDiscrepancies: boolean;
}

interface ComponentMethods {
  loadExamples(): Promise<void>;
  loadUsers(): Promise<void>;
  loadCategoryTypes(): Promise<void>;
  loadAnnotations(): Promise<void>;
  fetchManualDiscrepancies(): Promise<void>;
  hasDiscrepancy(exampleId: number): boolean;
  getLabelPercentages(item: ExampleWithAnnotations): Record<string, number>;
  getColor(percentage: number): string;
  removeUser(user: string): void;
  removeExample(example: ExampleItem): void;
  onSortByUpdate(value: string[]): void;
  onSortDescUpdate(value: boolean[]): void;
}

interface ComponentComputed {
  projectId: string;
  tableHeaders: Array<{
    text: string;
    value: string;
    sortable: boolean;
    align: string;
  }>;
  filteredAnnotations: ExampleWithAnnotations[];
}

export default Vue.extend<ComponentData, ComponentMethods, ComponentComputed>({
  layout: 'project',
  middleware: ['check-auth', 'auth', 'setCurrentProject'],

  data(): ComponentData {
    return {
      isLoading: false,
      error: null,
      examples: [],
      selectedExamples: [],
      users: [],
      selectedUsers: [],
      categoryTypes: [],
      annotations: [],
      sortBy: ['text'],
      sortDesc: [false],
      manualDiscrepancies: [],
      showOnlyDiscrepancies: false
    }
  },
  async fetch() {
    await Promise.all([
      this.loadExamples(),
      this.loadUsers(),
      this.loadCategoryTypes()
    ])
  },
  computed: {
    projectId() {
      return this.$route.params.id
    },
    tableHeaders() {
      const baseHeaders = [
        { text: 'Example', value: 'text', sortable: true, align: 'start' }
      ]
      
      if (this.selectedUsers.length > 0) {
        this.selectedUsers.forEach(user => {
          baseHeaders.push({
            text: user,
            value: user,
            sortable: false,
            align: 'start'
          })
        })
        baseHeaders.push({
          text: 'Label Percentages',
          value: 'label_percentages',
          sortable: false,
          align: 'start'
        })
      }
      
      return baseHeaders
    },
    filteredAnnotations() {
      let items = this.annotations
      
      if (this.selectedExamples.length === 0) {
        return []
      }
      
      items = items.filter((item: ExampleWithAnnotations) => 
        this.selectedExamples.some(example => example.id === item.id)
      )

      if (this.showOnlyDiscrepancies) {
        items = items.filter((item: ExampleWithAnnotations) => this.hasDiscrepancy(item.id))
      }

      return items
    }
  },

  watch: {
    selectedExamples: {
      handler() {
        this.loadAnnotations()
      },
      deep: true
    },
    selectedUsers: {
      handler() {
        this.loadAnnotations()
      },
      deep: true
    }
  },
  methods: {
    async loadExamples() {
      this.isLoading = true
      try {
        const response = await this.$services.example.list(this.projectId, {
          limit: '100',
          offset: '0',
          q: '',
          isChecked: '',
          ordering: '-id'
        })
        this.examples = response.items
      } catch (error: any) {
        console.error('Error loading examples:', error)
        if (error.response?.status === 500) {
          this.error = 'Database unavailable. Please try again later'
        } else {
          this.error = 'Error loading examples'
        }
      } finally {
        this.isLoading = false
      }
    },

    async loadUsers() {
      try {
        const response = await this.$repositories.user.list('')
        this.users = response.map(user => user.username)
      } catch (error: any) {
        console.error('Error loading users:', error)
        if (error.response?.status === 500) {
          this.error = 'Database unavailable. Please try again later'
        } else {
          this.error = 'Error loading users'
        }
      }
    },

    async loadCategoryTypes() {
      try {
        this.categoryTypes = await this.$services.categoryType.list(this.projectId)
      } catch (error: any) {
        console.error('Error loading category types:', error)
        if (error.response?.status === 500) {
          this.error = 'Database unavailable. Please try again later'
        } else {
          this.error = 'Error loading category types'
        }
      }
    },

    async loadAnnotations() {
      this.isLoading = true
      try {
        const annotations: ExampleWithAnnotations[] = []
        
        for (const example of this.examples) {
          const response = await this.$repositories.category.list(this.projectId, example.id)
          const exampleAnnotations: ExampleWithAnnotations = {
            id: example.id,
            text: example.text,
            annotations: {},
            labelPercentages: {}
          }

          // Group annotations by user
          const userAnnotations = new Map<string, string>()
          const labelCounts = new Map<string, number>()
          
          for (const annotation of response) {
            // Get user from the annotation
            const userResponse = await this.$repositories.user.list('')
            const user = userResponse.find(u => u.id === annotation.user)
            
            if (user) {
              const categoryType = this.categoryTypes.find(ct => ct.id === annotation.label)
              if (categoryType) {
                userAnnotations.set(user.username, categoryType.text)
                // Only count labels for selected users
                if (this.selectedUsers.includes(user.username)) {
                  const count = labelCounts.get(categoryType.text) || 0
                  labelCounts.set(categoryType.text, count + 1)
                }
              }
            }
          }

          // Calculate percentages based on selected users only
          const totalAnnotations = this.selectedUsers.length
          if (totalAnnotations > 0) {
            labelCounts.forEach((count, label) => {
              exampleAnnotations.labelPercentages[label] = (count / totalAnnotations) * 100
            })
          }

          // Add user annotations
          this.users.forEach(user => {
            exampleAnnotations.annotations[user] = userAnnotations.get(user) || ''
          })

          annotations.push(exampleAnnotations)
        }

        this.annotations = annotations
        console.log('Loaded annotations:', annotations)
      } catch (error: any) {
        console.error('Error loading annotations:', error)
        if (error.response?.status === 500) {
          this.error = 'Database unavailable. Please try again later'
        } else {
          this.error = 'Error loading annotations'
        }
      } finally {
        this.isLoading = false
      }
    },

    async fetchManualDiscrepancies() {
      try {
        const response = await axios.get(`/v1/projects/${this.projectId}/manual-discrepancies`)
        this.manualDiscrepancies = response.data
      } catch (error) {
        console.error('Error fetching manual discrepancies:', error)
      }
    },

    hasDiscrepancy(exampleId: number): boolean {
      return this.manualDiscrepancies.includes(exampleId)
    },

    getLabelPercentages(item: ExampleWithAnnotations) {
      return item.labelPercentages
    },

    getColor(percentage: number): string {
      if (percentage >= 80) return 'success'
      if (percentage >= 50) return 'warning'
      return 'error'
    },

    removeUser(user: string) {
      this.selectedUsers = this.selectedUsers.filter(u => u !== user)
    },

    removeExample(example: ExampleItem) {
      this.selectedExamples = this.selectedExamples.filter(e => e.id !== example.id)
    },

    onSortByUpdate(value: string[]) {
      this.sortBy = value
    },

    onSortDescUpdate(value: boolean[]) {
      this.sortDesc = value
    }
  }
})
</script>

<style scoped>
.example-cell {
  max-width: 300px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.discrepancy-row {
  background-color: rgba(255, 0, 0, 0.1);
}

.table-container {
  overflow-x: auto;
}
</style> 