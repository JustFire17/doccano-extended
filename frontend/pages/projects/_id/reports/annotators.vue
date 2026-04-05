<template>
  <v-card>
    <v-card-title class="text-h5">
      Annotator Reports
      <v-spacer></v-spacer>
      <v-chip color="info" outlined small>
        <v-icon left small>mdi-layers</v-icon>
        All Project Versions
      </v-chip>
    </v-card-title>
    <v-card-text>
      <v-row>
        <v-col cols="12" md="3">
          <v-card>
            <v-card-title class="subtitle-1">Filters</v-card-title>
            <v-card-text>
              <v-form ref="form">
                <!-- Date range filter -->
                <v-menu
                  v-model="datePickerStart"
                  :close-on-content-click="false"
                  transition="scale-transition"
                  min-width="auto"
                >
                  <template #activator="{ on, attrs }">
                    <v-text-field
                      :value="startDateText"
                      label="Start Date"
                      prepend-icon="mdi-calendar"
                      readonly
                      v-bind="attrs"
                      v-on="on"
                    >
                      <template #append>
                        <v-btn
                          v-if="startDateText !== 'All time'"
                          icon
                          small
                          @click="clearStartDate"
                        >
                          <v-icon>mdi-close</v-icon>
                        </v-btn>
                      </template>
                    </v-text-field>
                  </template>
                  <v-date-picker
                    v-model="filters.dateStart"
                    @input="updateStartDate"
                  >
                    <v-spacer></v-spacer>
                    <v-btn text color="error" @click="clearStartDate">Clear</v-btn>
                    <v-btn text color="primary" @click="datePickerStart = false">OK</v-btn>
                  </v-date-picker>
                </v-menu>

                <v-menu
                  v-model="datePickerEnd"
                  :close-on-content-click="false"
                  transition="scale-transition"
                  min-width="auto"
                >
                  <template #activator="{ on, attrs }">
                    <v-text-field
                      :value="endDateText"
                      label="End Date"
                      prepend-icon="mdi-calendar"
                      readonly
                      v-bind="attrs"
                      v-on="on"
                    >
                      <template #append>
                        <v-btn
                          v-if="endDateText !== 'Present'"
                          icon
                          small
                          @click="clearEndDate"
                        >
                          <v-icon>mdi-close</v-icon>
                        </v-btn>
                      </template>
                    </v-text-field>
                  </template>
                  <v-date-picker
                    v-model="filters.dateEnd"
                    @input="updateEndDate"
                  >
                    <v-spacer></v-spacer>
                    <v-btn text color="error" @click="clearEndDate">Clear</v-btn>
                    <v-btn text color="primary" @click="datePickerEnd = false">OK</v-btn>
                  </v-date-picker>
                </v-menu>

                <!-- Perspective filter (updated from Annotation Statistics) -->
                <v-select
                  v-model="filters.perspectiveId"
                  :items="perspectives"
                  item-text="name"
                  item-value="id"
                  label="Filter by Perspective"
                  multiple
                  chips
                  clearable
                  @change="onPerspectiveChange"
                ></v-select>

                <!-- Perspective value filter (updated from Annotation Statistics) -->
                <v-select
                  v-if="filters.perspectiveId && filters.perspectiveId.length > 0"
                  v-model="selectedPerspectiveValues"
                  :items="allPerspectiveValues"
                  label="Perspective Values"
                  multiple
                  chips
                  clearable
                  @change="applyFilters"
                ></v-select>

                <!-- User filter -->
                <v-select
                  v-model="filters.username"
                  :items="userOptions"
                  label="Annotator"
                  multiple
                  chips
                  clearable
                  @change="applyFilters"
                ></v-select>

                <!-- Example filter -->
                <v-select
                  v-model="filters.exampleId"
                  :items="exampleOptions"
                  label="Filter by Text"
                  item-text="display_text"
                  item-value="id"
                  multiple
                  chips
                  clearable
                  @change="applyFilters"
                ></v-select>

                <!-- Project Version filter -->
                <v-select
                  v-model="filters.projectVersion"
                  :items="versionOptions"
                  label="Filter by Project Version"
                  item-text="text"
                  item-value="value"
                  multiple
                  chips
                  clearable
                  @change="applyFilters"
                ></v-select>

                <!-- Button to apply filters -->
                <v-btn color="primary" class="mt-4" block :loading="isExporting" @click="applyFiltersAndExport">
                  Apply and Export
                </v-btn>
              </v-form>
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12" md="9">
          <v-tabs v-model="activeTab">
            <v-tab>Summary</v-tab>
            <v-tab>Detailed Data</v-tab>
          </v-tabs>

          <v-tabs-items v-model="activeTab">
            <!-- Summary Tab -->
            <v-tab-item>
              <v-card flat>
                <v-card-text>
                  <v-row>
                    <v-col cols="12" md="3">
                      <v-card class="pa-2" outlined>
                        <div class="text-center text-h6">Total Annotations</div>
                        <div class="text-center text-h3 font-weight-bold">{{ stats.totalAnnotations }}</div>
                      </v-card>
                    </v-col>
                    <v-col cols="12" md="3">
                      <v-card class="pa-2" outlined>
                        <div class="text-center text-h6">Active Annotators</div>
                        <div class="text-center text-h3 font-weight-bold">{{ stats.totalAnnotators }}</div>
                      </v-card>
                    </v-col>
                    <v-col cols="12" md="3">
                      <v-card class="pa-2" outlined>
                        <div class="text-center text-h6">Avg. Annotations/Day</div>
                        <div class="text-center text-h3 font-weight-bold">{{ stats.avgAnnotationsPerDay }}</div>
                      </v-card>
                    </v-col>
                    <v-col cols="12" md="3">
                      <v-card class="pa-2" outlined>
                        <div class="text-center text-h6">Project Versions</div>
                        <div class="text-center text-h3 font-weight-bold">
                          <span v-if="projectVersionsFound.length > 0">
                            {{ projectVersionsFound.join(', ') }}
                          </span>
                          <span v-else>-</span>
                        </div>
                      </v-card>
                    </v-col>
                  </v-row>

                  <v-card class="mt-4" outlined>
                    <v-card-title>Annotator Performance</v-card-title>
                    <v-card-text>
                      <v-data-table
                        :headers="summaryHeaders"
                        :items="annotatorStats"
                        :items-per-page="10"
                        class="elevation-1"
                      ></v-data-table>
                    </v-card-text>
                  </v-card>
                </v-card-text>
              </v-card>
            </v-tab-item>

            <!-- Detailed Data Tab -->
            <v-tab-item>
              <v-card flat>
                <v-card-text>
                  <v-data-table
                    :headers="detailedHeaders"
                    :items="annotationData"
                    :items-per-page="15"
                    class="elevation-1"
                    :loading="isLoading"
                    item-key="id"
                  >
                    <template #[`item.created_at`]="{ item }">
                      {{ formatDate(item.created_at) }}
                    </template>
                    <template #[`item.label_text`]="{ item }">
                      <v-chip
                        :color="item.backgroundColor || 'grey'"
                        text-color="white"
                        small
                      >
                        {{ item.label_text }}
                      </v-chip>
                    </template>
                  </v-data-table>
                </v-card-text>
              </v-card>
            </v-tab-item>
          </v-tabs-items>
        </v-col>
      </v-row>
    </v-card-text>

    <!-- Export Dialog -->
    <v-dialog v-model="exportDialog" max-width="400px">
      <v-card>
        <v-card-title class="headline">Export Options</v-card-title>
        <v-card-text>
          <v-checkbox v-model="exportOptions.pdf" label="Export as PDF"></v-checkbox>
          <v-checkbox v-model="exportOptions.csv" label="Export as CSV"></v-checkbox>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn color="red" text @click="closeExportDialog">Cancel</v-btn>
          <v-btn color="primary" text :disabled="!isExportOptionSelected" @click="exportData">Export</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-card>
</template>

<script lang="ts">
import Vue from 'vue'
import html2pdf from 'html2pdf.js'

interface AnnotationItem {
  id: number
  username: string
  created_at: string
  type: string
  example_text: string
  label_text: string
  example_id?: number
  label_id?: number
  project_version: number
  original_example_id: number
  perspective?: {
    id: number
    value: string
  }
}

interface AnnotatorStats {
  username: string
  totalAnnotations: number
  dates: Set<string>
  lastActive: string | null
}

interface Filters {
  dateStart: string | null
  dateEnd: string | null
  perspectiveId: number[] | null
  perspectiveValue: string[] | null
  username: string[] | null
  exampleId: number[] | null
  projectVersion: number[] | null
}

interface AnnotatorData {
  isLoading: boolean
  isExporting: boolean
  activeTab: number
  datePickerStart: boolean
  datePickerEnd: boolean
  hasPerspectives: boolean
  startDateText: string
  endDateText: string
  filters: Filters
  perspectives: any[]
  perspectiveValues: string[]
  selectedPerspectiveValues: string[]
  allPerspectiveValues: string[]
  perspectiveValuesMap: Record<number, string[]>
  annotationData: AnnotationItem[]
  summaryHeaders: Array<{text: string, value: string}>
  detailedHeaders: Array<{text: string, value: string, width?: string}>
  userOptions: string[]
  exampleOptions: Array<{text: string, display_text: string, id: number}>
  versionOptions: Array<{text: string, value: number}>
  exportDialog: boolean
  exportOptions: {
    pdf: boolean
    csv: boolean
  }
}

export default Vue.extend<AnnotatorData, {
  formatDate(dateString: string): string
  loadPerspectives(): Promise<void>
  onPerspectiveChange(): Promise<void>
  fetchAnnotations(): Promise<void>
  applyFilters(): void
  applyFiltersAndExport(): Promise<void>
  clearStartDate(): void
  clearEndDate(): void
  updateStartDate(): void
  updateEndDate(): void
  populateUserOptions(data: AnnotationItem[]): void
  populateExampleOptions(data: AnnotationItem[]): void
  populateVersionOptions(data: AnnotationItem[]): void
  openExportDialog(): void
  closeExportDialog(): void
  exportData(): Promise<void>
  exportToPDF(): Promise<void>
  exportToCSV(): Promise<void>
}, {
  projectId: string
  dateRangeText: {start: string, end: string}
  projectVersionsFound: number[]
  stats: {totalAnnotations: number, totalAnnotators: number, avgAnnotationsPerDay: number}
  annotatorStats: Array<{username: string, totalAnnotations: number, avgPerDay: number, lastActive: string}>
  isExportOptionSelected: boolean
}, {}>({
  layout: 'project',

  middleware: ['check-auth', 'auth', 'setCurrentProject'],

  data() {
    return {
      isLoading: false,
      isExporting: false,
      activeTab: 0,
      datePickerStart: false,
      datePickerEnd: false,
      hasPerspectives: true,
      startDateText: 'All time',
      endDateText: 'Present',
      filters: {
        dateStart: null,
        dateEnd: null,
        perspectiveId: null,
        perspectiveValue: null,
        username: null,
        exampleId: null,
        projectVersion: null
      } as Filters,
      perspectives: [] as any[],
      perspectiveValues: [] as string[],
      selectedPerspectiveValues: [] as string[],
      annotations: [] as any[],
      allPerspectiveValues: [] as string[],
      perspectiveValuesMap: {},
      annotationData: [] as AnnotationItem[],
      summaryHeaders: [
        { text: 'Annotator', value: 'username' },
        { text: 'Total Annotations', value: 'totalAnnotations' },
        { text: 'Avg. per Day', value: 'avgPerDay' },
        { text: 'Last Active', value: 'lastActive' }
      ],
      detailedHeaders: [
        { text: 'Annotator', value: 'username' },
        { text: 'Date', value: 'created_at' },
        { text: 'Type', value: 'type' },
        { text: 'Example', value: 'example_text', width: '40%' },
        { text: 'Label', value: 'label_text' },
        { text: 'Version', value: 'project_version' }
      ],
      userOptions: [] as string[],
      exampleOptions: [] as Array<{text: string, display_text: string, id: number}>,
      versionOptions: [] as Array<{text: string, value: number}>,
      exportDialog: false,
      exportOptions: {
        pdf: false,
        csv: false
      }
    }
  },

  computed: {
    projectId(): string {
      return this.$route.params.id
    },
    dateRangeText(): {start: string, end: string} {
      return {
        start: this.startDateText,
        end: this.endDateText
      }
    },
    projectVersionsFound(): number[] {
      const versions = [...new Set(this.annotationData.map(item => item.project_version))]
      return versions.sort((a, b) => a - b)
    },
    stats() {
      // Calculate statistics from the annotationData
      const totalAnnotations = this.annotationData.length
      
      // Get unique annotators
      const annotators = [...new Set(this.annotationData.map((item: AnnotationItem) => item.username))]
      const totalAnnotators = annotators.length
      
      // Calculate average annotations per day
      // In a real implementation, you would use actual date data
      const avgAnnotationsPerDay = totalAnnotations > 0 ? Math.round(totalAnnotations / 30) : 0
      
      return {
        totalAnnotations,
        totalAnnotators,
        avgAnnotationsPerDay
      }
    },
    annotatorStats() {
      if (!this.annotationData.length) return []
      
      // Group by annotator and calculate stats
      const annotators: Record<string, AnnotatorStats> = {}
      this.annotationData.forEach(item => {
        if (!annotators[item.username]) {
          annotators[item.username] = {
            username: item.username,
            totalAnnotations: 0,
            dates: new Set<string>(),
            lastActive: null
          }
        }
        
        annotators[item.username].totalAnnotations++
        annotators[item.username].dates.add(item.created_at.split('T')[0])
        
        // Track last active date
        const itemDate = new Date(item.created_at)
        if (!annotators[item.username].lastActive || 
            (annotators[item.username].lastActive && 
             itemDate > new Date(annotators[item.username].lastActive as string))) {
          annotators[item.username].lastActive = item.created_at
        }
      })
      
      // Convert to array and calculate average per day
      return Object.values(annotators).map(annotator => {
        const totalDays = annotator.dates.size
        return {
          username: annotator.username,
          totalAnnotations: annotator.totalAnnotations,
          avgPerDay: totalDays ? Math.round(annotator.totalAnnotations / totalDays) : 0,
          lastActive: this.formatDate(annotator.lastActive || '')
        }
      })
    },
    isExportOptionSelected() {
      return this.exportOptions.pdf || this.exportOptions.csv
    }
  },

  async mounted() {
    try {
      // Initialize date texts
      this.startDateText = this.filters.dateStart ? this.formatDate(this.filters.dateStart) : 'All time'
      this.endDateText = this.filters.dateEnd ? this.formatDate(this.filters.dateEnd) : 'Present'
      
      // Load perspectives
      await this.loadPerspectives()
      
      // Fetch real annotations
      await this.fetchAnnotations()
    } catch (error: any) {
      console.error('Error initializing data:', error)
    }
  },

  methods: {
    async loadPerspectives() {
      try {
        // Initialize perspectives to an empty array by default
        this.perspectives = []
        this.hasPerspectives = false
        
        // Check if the project has perspectives associated
        const project = await this.$services.project.findById(this.projectId)
        
        if (project && project.perspective_associated) {
          // Load perspectives
          const perspectives = await this.$services.perspective.list(this.projectId)
          
          // Check if perspectives is valid and not empty
          if (perspectives && Array.isArray(perspectives)) {
            this.perspectives = perspectives
            this.hasPerspectives = perspectives.length > 0
          }
        }
      } catch (error: any) {
        console.error('Error loading perspectives:', error)
        if (error?.response?.status === 500) {
          alert('Database unavailable. Please try again later')
        } else {
          console.error('Error loading perspectives:', error)
        }
        
        // Ensure perspectives is always an array even in case of error
        this.perspectives = []
        this.hasPerspectives = false
      }
    },

    async fetchAnnotations() {
      this.isLoading = true
      try {
        const filters = {
          dateStart: this.filters.dateStart,
          dateEnd: this.filters.dateEnd,
          perspectiveId: this.filters.perspectiveId?.join(',') || null,
          perspectiveValue: this.selectedPerspectiveValues?.join(',') || null,
          username: this.filters.username?.join(',') || null,
          exampleId: this.filters.exampleId?.join(',') || null,
          projectVersion: this.filters.projectVersion?.join(',') || null
        }
        
        try {
          const response: any = await this.$services.report.getAnnotatorReports(this.projectId, filters)
          
          // Handle both old and new response formats
          if (response && response.annotations) {
            // New format with separate filter data
            this.annotationData = response.annotations
            
            if (response.unique_examples) {
              this.exampleOptions = response.unique_examples
            } else {
              this.populateExampleOptions(this.annotationData)
            }
            
            if (response.project_versions) {
              this.versionOptions = response.project_versions.map((v: number) => ({
                text: `Version ${v}`,
                value: v
              }))
            } else {
              this.populateVersionOptions(this.annotationData)
            }
          } else {
            // Old format - direct array
            this.annotationData = Array.isArray(response) ? response : []
            this.populateExampleOptions(this.annotationData)
            this.populateVersionOptions(this.annotationData)
          }
          
          this.populateUserOptions(this.annotationData)
        } catch (error: any) {
          console.error('API call failed:', error)
          if (error?.response?.status === 500) {
            alert('Database unavailable. Please try again later')
          } else {
            console.error('Error fetching annotations:', error)
          }
          this.annotationData = []
        }
      } catch (error: any) {
        console.error('Error fetching annotations:', error)
        if (error?.response?.status === 500) {
          alert('Database unavailable. Please try again later')
        } else {
          console.error('Error fetching annotations:', error)
        }
        this.annotationData = []
      } finally {
        this.isLoading = false
      }
    },

    applyFilters() {
      this.fetchAnnotations()
    },

    async applyFiltersAndExport() {
      this.isExporting = true
      try {
        // Primeiro aplicar os filtros
        await this.fetchAnnotations()
        
        // Depois fazer o download de ambos os formatos
        if (this.annotationData.length > 0) {
          await this.exportToPDF()
          await this.exportToCSV()
        } else {
          // Mostrar mensagem se não houver dados para exportar
          alert('No data to export after applying filters')
        }
      } catch (error: any) {
        if (error?.response?.status === 500) {
          alert('Database unavailable. Please try again later')
        } else {
          console.error('Error applying filters and downloading:', error)
        }
      } finally {
        this.isExporting = false
      }
    },

    formatDate(dateString: string): string {
      if (!dateString) return ''
      const date = new Date(dateString)
      
      // Format: YYYY-MM-DD HH:MM
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      const hours = String(date.getHours()).padStart(2, '0')
      const minutes = String(date.getMinutes()).padStart(2, '0')
      
      return `${year}-${month}-${day} ${hours}:${minutes}`
    },

    updateStartDate() {
      if (this.filters.dateStart) {
        this.startDateText = this.formatDate(this.filters.dateStart)
      } else {
        this.startDateText = 'All time'
      }
      this.datePickerStart = false
      this.applyFilters()
    },

    updateEndDate() {
      if (this.filters.dateEnd) {
        this.endDateText = this.formatDate(this.filters.dateEnd)
      } else {
        this.endDateText = 'Present'
      }
      this.datePickerEnd = false
      this.applyFilters()
    },

    clearStartDate() {
      this.filters.dateStart = null
      this.startDateText = 'All time'
      // Forçar a atualização da interface
      this.$forceUpdate()
      this.$nextTick(() => {
        this.applyFilters()
      })
    },

    clearEndDate() {
      this.filters.dateEnd = null
      this.endDateText = 'Present'
      // Forçar a atualização da interface
      this.$forceUpdate()
      this.$nextTick(() => {
        this.applyFilters()
      })
    },

    async onPerspectiveChange() {
      this.selectedPerspectiveValues = []
      this.allPerspectiveValues = []
      this.perspectiveValuesMap = {}

      if (this.filters.perspectiveId && this.filters.perspectiveId.length > 0) {
        try {
          const allValues: Record<string, string[]> = await this.$services.perspective.getAllFilledValues(this.projectId)
      
          this.filters.perspectiveId.forEach((id: number) => {
            const perspectiveId = String(id)
            if (allValues[perspectiveId]) {
              this.perspectiveValuesMap[id] = allValues[perspectiveId]
              allValues[perspectiveId].forEach((value: string) => {
                if (!this.allPerspectiveValues.includes(value)) {
                  this.allPerspectiveValues.push(value)
                }
              })
            }
          })
        } catch (error) {
          console.error('Error loading perspective values:', error)
        }
      }
    },

    // Add method to populate user options from data
    populateUserOptions(data: AnnotationItem[]) {
      // Extract unique usernames
      const uniqueUsers = [...new Set(data.map(item => item.username))]
      this.userOptions = uniqueUsers.sort()
    },

    populateExampleOptions(data: AnnotationItem[]) {
      // Extract unique examples based on example ID
      const examples = new Map<number, {text: string, display_text: string, id: number}>()
      
      data.forEach(item => {
        if (item.example_id && !examples.has(item.example_id)) {
          // Use only the first 50 characters of text to keep dropdown items short
          const shortText = item.example_text.length > 50 
            ? item.example_text.substring(0, 50) + '...' 
            : item.example_text
          examples.set(item.example_id, {
            text: item.example_text,
            display_text: shortText,
            id: item.example_id
          })
        }
      })
      
      // Convert to array of options
      this.exampleOptions = Array.from(examples.values())
        .sort((a, b) => a.display_text.localeCompare(b.display_text))
    },

    populateVersionOptions(data: AnnotationItem[]) {
      // Extract unique project versions
      const versions = [...new Set(data.map(item => item.project_version))]
      this.versionOptions = versions.map((v: number) => ({
        text: `Version ${v}`,
        value: v
      }))
    },

    openExportDialog() {
      this.exportDialog = true
    },

    closeExportDialog() {
      this.exportDialog = false
      this.exportOptions.pdf = false
      this.exportOptions.csv = false
    },

    async exportData() {
      this.isExporting = true
      try {
        if (this.exportOptions.pdf) {
          await this.exportToPDF()
        }
        if (this.exportOptions.csv) {
          await this.exportToCSV()
        }
        this.closeExportDialog()
      } catch (error: any) {
        if (error?.response?.status === 500) {
          alert('Database unavailable. Please try again later')
        } else {
          console.error('Error during export:', error)
        }
      } finally {
        this.isExporting = false
      }
    },

    async exportToPDF(): Promise<void> {
      try {
        const content = document.createElement('div')
        
        // Add title
        const title = document.createElement('h1')
        title.textContent = 'Annotator Reports - Detailed Data'
        title.style.marginBottom = '20px'
        content.appendChild(title)

        // Add filters info if applied
        const filtersInfo = document.createElement('div')
        filtersInfo.style.marginBottom = '20px'
        let filtersText = 'Applied Filters: '
        const appliedFilters = []
        
        if (this.filters.dateStart) appliedFilters.push(`Start Date: ${this.startDateText}`)
        if (this.filters.dateEnd) appliedFilters.push(`End Date: ${this.endDateText}`)
        if (this.filters.perspectiveId && this.filters.perspectiveId.length > 0) {
          const perspectiveNames = this.filters.perspectiveId.map(id => {
            const perspective = this.perspectives.find(p => p.id === id)
            return perspective ? perspective.name : id
          }).join(', ')
          appliedFilters.push(`Perspectives: ${perspectiveNames}`)
        }
        if (this.selectedPerspectiveValues && this.selectedPerspectiveValues.length > 0) {
          appliedFilters.push(`Perspective Values: ${this.selectedPerspectiveValues.join(', ')}`)
        }
        if (this.filters.username && this.filters.username.length > 0) {
          appliedFilters.push(`Annotators: ${this.filters.username.join(', ')}`)
        }
        if (this.filters.exampleId && this.filters.exampleId.length > 0) {
          appliedFilters.push(`Examples: ${this.filters.exampleId.length} selected`)
        }
        
        filtersText += appliedFilters.length > 0 ? appliedFilters.join(' | ') : 'None'
        filtersInfo.textContent = filtersText
        filtersInfo.style.fontSize = '12px'
        filtersInfo.style.color = '#666'
        content.appendChild(filtersInfo)

        // Add summary statistics
        const statsDiv = document.createElement('div')
        statsDiv.style.marginBottom = '30px'
        statsDiv.innerHTML = `
          <h3>Summary Statistics</h3>
          <p><strong>Total Annotations:</strong> ${this.stats.totalAnnotations}</p>
          <p><strong>Active Annotators:</strong> ${this.stats.totalAnnotators}</p>
          <p><strong>Average Annotations/Day:</strong> ${this.stats.avgAnnotationsPerDay}</p>
        `
        content.appendChild(statsDiv)

        // Group data by version and sort
        const groupedByVersion = new Map<number, AnnotationItem[]>()
        this.annotationData.forEach(item => {
          if (!groupedByVersion.has(item.project_version)) {
            groupedByVersion.set(item.project_version, [])
          }
          groupedByVersion.get(item.project_version)!.push(item)
        })

        // Sort versions
        const sortedVersions = Array.from(groupedByVersion.keys()).sort((a, b) => a - b)

        // Add detailed data by version
        sortedVersions.forEach(version => {
          const versionData = groupedByVersion.get(version)!
          
          // Add version header
          const versionTitle = document.createElement('h3')
          versionTitle.textContent = `Version ${version} (${versionData.length} annotations)`
          versionTitle.style.marginTop = '30px'
          versionTitle.style.marginBottom = '15px'
          versionTitle.style.color = '#1976d2'
          versionTitle.style.borderBottom = '2px solid #1976d2'
          versionTitle.style.paddingBottom = '5px'
          content.appendChild(versionTitle)

          const table = document.createElement('table')
          table.style.width = '100%'
          table.style.borderCollapse = 'collapse'
          table.style.fontSize = '10px'
          table.style.marginBottom = '20px'

          // Add headers for detailed data
          const headers = document.createElement('tr')
          headers.style.backgroundColor = '#f5f5f5'
          this.detailedHeaders.forEach(header => {
            const th = document.createElement('th')
            th.textContent = header.text
            th.style.border = '1px solid #ddd'
            th.style.padding = '8px'
            th.style.textAlign = 'left'
            th.style.fontWeight = 'bold'
            headers.appendChild(th)
          })
          table.appendChild(headers)

          // Add data rows for this version
          versionData.forEach((item: AnnotationItem, index: number) => {
            const row = document.createElement('tr')
            if (index % 2 === 1) {
              row.style.backgroundColor = '#f9f9f9'
            }
            
            // Annotator
            const annotatorCell = document.createElement('td')
            annotatorCell.textContent = item.username
            annotatorCell.style.border = '1px solid #ddd'
            annotatorCell.style.padding = '6px'
            row.appendChild(annotatorCell)
            
            // Date
            const dateCell = document.createElement('td')
            dateCell.textContent = this.formatDate(item.created_at)
            dateCell.style.border = '1px solid #ddd'
            dateCell.style.padding = '6px'
            row.appendChild(dateCell)
            
            // Type
            const typeCell = document.createElement('td')
            typeCell.textContent = item.type
            typeCell.style.border = '1px solid #ddd'
            typeCell.style.padding = '6px'
            row.appendChild(typeCell)
            
            // Example (truncated for PDF)
            const exampleCell = document.createElement('td')
            const truncatedText = item.example_text.length > 80 
              ? item.example_text.substring(0, 80) + '...' 
              : item.example_text
            exampleCell.textContent = truncatedText
            exampleCell.style.border = '1px solid #ddd'
            exampleCell.style.padding = '6px'
            exampleCell.style.maxWidth = '300px'
            exampleCell.style.wordWrap = 'break-word'
            row.appendChild(exampleCell)
            
            // Label
            const labelCell = document.createElement('td')
            labelCell.textContent = item.label_text
            labelCell.style.border = '1px solid #ddd'
            labelCell.style.padding = '6px'
            row.appendChild(labelCell)
            
            // Version
            const versionCell = document.createElement('td')
            versionCell.textContent = item.project_version.toString()
            versionCell.style.border = '1px solid #ddd'
            versionCell.style.padding = '6px'
            row.appendChild(versionCell)
            
            table.appendChild(row)
          })
          content.appendChild(table)
        })

        // Add footer with export info
        const footer = document.createElement('div')
        footer.style.marginTop = '20px'
        footer.style.fontSize = '10px'
        footer.style.color = '#888'
        const versionList = sortedVersions.map(v => `Version ${v}`).join(', ')
        footer.textContent = `Exported on ${new Date().toLocaleString()} | Total records: ${this.annotationData.length} | Versions: ${versionList}`
        content.appendChild(footer)

        // Configure PDF options
        const options = {
          margin: 10,
          filename: `annotator-report-detailed-${new Date().toISOString().slice(0,10)}.pdf`,
          image: { type: 'jpeg', quality: 0.98 },
          html2canvas: { scale: 1.5, useCORS: true },
          jsPDF: { unit: 'mm', format: 'a4', orientation: 'landscape' } // Landscape for better table fit
        }

        // Generate PDF
        await html2pdf().from(content).set(options).save()
      } catch (error: any) {
        if (error?.response?.status === 500) {
          alert('Database unavailable. Please try again later')
        } else {
          console.error('Error exporting to PDF:', error)
        }
        throw error; // Re-throw to be handled by the parent function
      }
    },

    async exportToCSV(): Promise<void> {
      try {
        // Cabeçalho do CSV
        const headers = ['Annotator', 'Date', 'Type', 'Example', 'Label', 'Version']
        const rows: string[] = []

        // Agrupar por versão e ordenar
        const groupedByVersion = new Map<number, AnnotationItem[]>()
        this.annotationData.forEach(item => {
          if (!groupedByVersion.has(item.project_version)) {
            groupedByVersion.set(item.project_version, [])
          }
          groupedByVersion.get(item.project_version)!.push(item)
        })
        const sortedVersions = Array.from(groupedByVersion.keys()).sort((a, b) => a - b)

        // Adicionar linhas dos dados
        sortedVersions.forEach(version => {
          const versionData = groupedByVersion.get(version)!
          versionData.forEach(item => {
            // Função para escapar campos CSV
            const escapeCSV = (field: string): string => {
              if (field == null) return '""'
              const str = String(field)
              if (str.includes(',') || str.includes('"') || str.includes('\n') || str.includes('\r')) {
                return '"' + str.replace(/"/g, '""') + '"'
              }
              return str
            }
            rows.push([
              escapeCSV(item.username),
              escapeCSV(this.formatDate(item.created_at)),
              escapeCSV(item.type),
              escapeCSV(item.example_text),
              escapeCSV(item.label_text),
              escapeCSV(item.project_version.toString())
            ].join(','))
          })
        })

        // Montar o conteúdo final
        const csvContent = [headers.join(','), ...rows].join('\n')
        const BOM = '\uFEFF'
        const csvWithBOM = BOM + csvContent

        // Criar e baixar o arquivo
        const blob = new Blob([csvWithBOM], { type: 'text/csv;charset=utf-8' })
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.setAttribute('hidden', '')
        a.setAttribute('href', url)
        a.setAttribute('download', `annotator-report-detailed-${new Date().toISOString().slice(0,10)}.csv`)
        document.body.appendChild(a)
        await new Promise<void>(resolve => {
          a.click()
          setTimeout(() => {
            window.URL.revokeObjectURL(url)
            document.body.removeChild(a)
            resolve()
          }, 100)
        })
      } catch (error: any) {
        if (error?.response?.status === 500) {
          alert('Database unavailable. Please try again later')
        } else {
          console.error('Error exporting data:', error)
        }
        throw error
      }
    }
  },


})
</script>

<style scoped>
.v-card__text {
  padding-top: 0;
}
</style> 