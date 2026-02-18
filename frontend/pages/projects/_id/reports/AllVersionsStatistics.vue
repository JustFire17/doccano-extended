<template>
  <div>
    <v-card>
      <v-card-title>
        <span class="headline">All-Versions Statistics</span>
        <v-spacer></v-spacer>
        <v-btn
          color="primary"
          :loading="loading"
          @click="showStatistics"
        >
          Show Statistics
        </v-btn>

        <v-btn color="primary" @click="openExportDialog">
          Export
        </v-btn>
      </v-card-title>

      <v-card-text>
        <!-- Filters -->
        <v-row>
          <v-col cols="12" md="4">
            <v-select
              v-model="filters.versions"
              :items="projectVersions"
              label="Filter by Versions"
              item-text="displayVersion"
              item-value="id"
              multiple
              chips
              clearable
              :menu-props="{ maxHeight: '400px' }"
              class="filter-select"
              @change="showStatistics"
            ></v-select>
          </v-col>

          <v-col cols="12" md="4">
            <v-select
              v-model="filters.annotation"
              :items="annotations"
              label="Filter by Annotation"
              item-text="text"
              item-value="id"
              multiple
              chips
              clearable
              :menu-props="{ maxHeight: '400px' }"
              class="filter-select"
              @change="showStatistics"
            ></v-select>
          </v-col>

          <v-col cols="12" md="4">
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
          </v-col>

          <v-col v-if="filters.perspectiveId && filters.perspectiveId.length > 0" cols="12" md="4">
            <v-select
              v-model="selectedPerspectiveValues"
              :items="allPerspectiveValues"
              label="Perspective Values"
              multiple
              chips
              clearable
              @change="onPerspectiveValuesChange"
            ></v-select>
          </v-col>
        </v-row>

        <!-- Statistics Cards -->
        <v-row v-if="!loading && showResults">
          <v-col v-for="version in annotationResults" :key="version.version_id" cols="12">
            <v-card class="mb-4">
              <v-card-title>
                Version {{ version.version_number }}
                <v-chip
                  v-if="version.is_current_version"
                  color="primary"
                  small
                  class="ml-2"
                >
                  Current
                </v-chip>
              </v-card-title>
              <v-card-text>
                <v-row v-for="(annotation, annotationIndex) in version.annotations" :key="annotationIndex">
                  <v-col cols="12">
                    <v-card outlined class="mb-4">
                      <v-card-title>Annotation {{ annotationIndex + 1 }}</v-card-title>
                      <v-card-text>
                        <v-row align="start">
                          <!-- Text -->
                          <v-col cols="12" md="6">
                            <div class="subtitle-1 font-weight-bold mb-2">Annotation Text</div>
                            <div>{{ annotation.text }}</div>
                          </v-col>
                          <!-- Discrepancy and Labels -->
                          <v-col cols="12" md="6" class="d-flex flex-column justify-start">
                            <div class="mb-2">
                              <v-chip v-if="annotation.discrepancy" color="error" class="ml-2">
                                Discrepancy
                              </v-chip>
                              <v-chip v-if="annotation.discrepancy" :color="annotation.discrepancy_status === 'Reported' ? 'success' : 'warning'" class="ml-2">
                                {{ annotation.discrepancy_status }}
                              </v-chip>
                            </div>
                            <div class="label-stats w-100">
                              <div class="label-bars">
                                <div 
                                  v-for="label in annotation.labels" 
                                  :key="label.id"
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
                          </v-col>
                        </v-row>
                      </v-card-text>
                    </v-card>
                  </v-col>
                </v-row>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <v-row v-if="loading" justify="center" align="center">
          <v-col cols="12" class="text-center">
            <v-progress-circular
              indeterminate
              color="primary"
              size="64"
            ></v-progress-circular>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Export Dialog -->
    <v-dialog v-model="exportDialog" max-width="400px">
      <v-card-title class="headline">Export Options</v-card-title>
      <v-card-text>
        <v-checkbox
          v-model="exportFormats"
          label="PDF"
          value="pdf"
          hide-details
        />
        <v-checkbox
          v-model="exportFormats"
          label="CSV"
          value="csv"
          hide-details
        />
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn color="red" text @click="closeExportDialog">Cancel</v-btn>
        <v-btn color="primary" text @click="exportData">Export</v-btn>
      </v-card-actions>
    </v-dialog>
  </div>
</template>

<script lang="ts">
import Vue from 'vue'
import { mapGetters } from 'vuex'
import html2pdf from 'html2pdf.js'
import { Project } from '~/domain/models/project/project'

interface Label {
  id: number
  text: string
  backgroundColor: string
  count: number
  percentage: number
}

interface Annotation {
  id: number
  text: string
  labels: Label[]
  discrepancy?: boolean
  discrepancy_status?: string | null
}

interface VersionData {
  version_id: number
  version_number: number
  is_current_version: boolean
  annotations: Annotation[]
}

interface StatisticsResponse {
  versions: VersionData[]
}

interface PerspectiveDTO {
  id: number
  name: string
  type: string
  options: string
}

interface PerspectiveValues {
  [key: string]: string[]
}

export default Vue.extend({
  layout: 'project',

  middleware: ['check-auth', 'auth', 'setCurrentProject'],

  data() {
    return {
      loading: false,
      showResults: false,
      exportDialog: false,
      exportFormats: ['pdf'],
      filters: {
        versions: [] as number[],
        annotation: [] as number[],
        perspectiveId: [] as number[],
      },
      selectedPerspectiveValues: [] as string[],
      annotations: [] as any[],
      perspectives: [] as PerspectiveDTO[],
      allPerspectiveValues: [] as string[],
      perspectiveValuesMap: {} as { [key: number]: string[] },
      annotationResults: [] as StatisticsResponse['versions'],
      currentProject: null as any,
      projectVersions: [] as Project[],
      error: null as string | null
    }
  },

  computed: {
    ...mapGetters('projects', ['project']),
    projectId(): string {
      return this.$route.params.id
    }
  },

  async created() {
    await Promise.all([
      this.loadAnnotations(),
      this.loadPerspectives(),
      this.loadProject(),
      this.loadProjectVersions()
    ])
  },

  methods: {
    async loadProjectVersions() {
      try {
        this.projectVersions = await this.$services.project.getProjectVersions(this.projectId)
      } catch (error: any) {
        if (error?.response?.status === 500) {
          alert('Database unavailable. Please try again later')
        } else {
          console.error('Error loading project versions:', error)
        }
        this.projectVersions = []
      }
    },

    async loadAnnotations() {
      try {
        const response = await this.$services.example.list(this.projectId, {
          limit: '1000',
          offset: '0'
        })
        this.annotations = response.items.map(item => ({
          id: item.id,
          text: item.text || item.filename,
          meta: item.meta || {}
        }))
      } catch (error: any) {
        if (error?.response?.status === 500) {
          alert('Database unavailable. Please try again later')
        } else {
          console.error('Error loading annotations:', error)
        }
        this.annotations = []
      }
    },

    async loadPerspectives() {
      try {
        const response = await this.$services.perspective.list(this.projectId)
        this.perspectives = response || []
      } catch (error: any) {
        if (error?.response?.status === 500) {
          alert('Database unavailable. Please try again later')
        } else {
          console.error('Error loading perspectives:', error)
        }
        this.perspectives = []
      }
    },

    async loadProject() {
      try {
        this.currentProject = await this.$services.project.findById(this.projectId)
      } catch (error: any) {
        if (error?.response?.status === 500) {
          alert('Database unavailable. Please try again later')
        } else {
          console.error('Error loading project:', error)
        }
      }
    },

    async onPerspectiveChange() {
      this.selectedPerspectiveValues = []
      this.allPerspectiveValues = []
      this.perspectiveValuesMap = {}
      this.error = null

      if (this.filters.perspectiveId && this.filters.perspectiveId.length > 0) {
        try {
          const allValues = await this.$services.perspective.getAllFilledValues(this.projectId) as PerspectiveValues
      
          this.filters.perspectiveId.forEach(id => {
            const perspectiveId = String(id)
            if (allValues[perspectiveId]) {
              this.perspectiveValuesMap[id] = allValues[perspectiveId]
              allValues[perspectiveId].forEach(value => {
                if (!this.allPerspectiveValues.includes(value)) {
                  this.allPerspectiveValues.push(value)
                }
              })
            }
          })
        } catch (error) {
          console.error('Error loading perspective values:', error)
          this.error = 'Error loading perspective values. Please try again.'
        }
      }
    },

    onPerspectiveValuesChange() {
      this.showStatistics()
    },

    async showStatistics() {
      this.loading = true
      this.error = null
      try {
        const params = new URLSearchParams()
        
        if (this.filters.versions.length > 0) {
          this.filters.versions.forEach(id => {
            params.append('version_ids', id.toString())
          })
        }
        
        if (this.filters.annotation.length > 0) {
          this.filters.annotation.forEach(id => {
            params.append('annotation_ids', id.toString())
          })
        }
        
        if (this.filters.perspectiveId && this.selectedPerspectiveValues) {
          this.filters.perspectiveId.forEach(perspectiveId => {
            params.append('perspective_ids', perspectiveId.toString())
          })
          
          this.selectedPerspectiveValues.forEach(value => {
            params.append('perspective_values', value)
          })
        }

        const response = await this.$services.project.getAnnotationStatisticsWithVersion(
          this.projectId, 
          params.toString()
        ) as StatisticsResponse
        
        this.annotationResults = response.versions
        this.showResults = true
      } catch (error: any) {
        console.error('Error fetching statistics:', error)
        if (error.response?.status === 500) {
          this.error = 'Database unavailable. Please try again later'
        } else {
          this.error = 'Error fetching statistics. Please try again.'
        }
        this.annotationResults = []
      } finally {
        this.loading = false
      }
    },

    openExportDialog() {
      this.exportDialog = true
    },

    closeExportDialog() {
      this.exportDialog = false
    },

    async exportData() {
      let success = false
      let errorOccurred = false
      if (this.exportFormats.includes('pdf')) {
        try {
          await this.exportToPDF()
          success = true
        } catch (error) {
          console.error('Error exporting PDF:', error)
          errorOccurred = true
        }
      }
      if (this.exportFormats.includes('csv')) {
        try {
          this.exportToCSV()
          success = true
        } catch (error) {
          console.error('Error exporting CSV:', error)
          errorOccurred = true
        }
      }
      if (success) alert('Exported successfully!')
      if (errorOccurred) alert('Failed to export some data.')
      this.closeExportDialog()
    },

    async exportToPDF() {
      try {
        // Montar os filtros aplicados
        let filtersHtml = ''
        if (this.filters.versions.length > 0) {
          const selectedVersions = this.projectVersions.filter(v => this.filters.versions.includes(v.id))
          filtersHtml += `<div><strong>Filtered Versions:</strong> ${selectedVersions.map(v => v.displayVersion).join(', ')}</div>`
        }
        if (this.filters.annotation.length > 0) {
          const selectedAnnotations = this.annotations.filter(a => this.filters.annotation.includes(a.id))
          filtersHtml += `<div><strong>Filtered Annotations:</strong> ${selectedAnnotations.map(a => a.text).join(', ')}</div>`
        }
        if (this.filters.perspectiveId.length > 0) {
          const selectedPerspectives = this.perspectives.filter(p => this.filters.perspectiveId.includes(p.id))
          filtersHtml += `<div><strong>Filtered Perspectives:</strong> ${selectedPerspectives.map(p => p.name).join(', ')}</div>`
        }
        if (this.selectedPerspectiveValues.length > 0) {
          filtersHtml += `<div><strong>Perspective Values:</strong> ${this.selectedPerspectiveValues.join(', ')}</div>`
        }

        const element = document.createElement('div')
        element.innerHTML = `
          <h1>All-Versions Statistics</h1>
          <h2>Project: ${this.currentProject.name}</h2>
          <div style='margin-bottom: 40px;'>${filtersHtml}</div>
          <div style='margin-top: 20px;'>
            ${this.annotationResults.map(version => `
              <div style='margin-bottom: 50px; page-break-inside: avoid;'>
                <h3>Version ${version.version_number}${version.is_current_version ? ' (Current)' : ''}</h3>
                ${version.annotations.map((annotation, index) => `
                  <div style='margin-bottom: 30px;'>
                    <h4>Annotation ${index + 1}</h4>
                    <p><strong>Text:</strong> ${annotation.text}</p>
                    ${annotation.discrepancy ? `<div style='margin-bottom: 8px;'><span style='color: #e53935; font-weight: bold;'>Discrepancy</span> <span style='color: ${annotation.discrepancy_status === 'Reported' ? '#43a047' : '#ffa000'}; font-weight: bold;'>${annotation.discrepancy_status}</span></div>` : ''}
                    <div style='margin-top: 10px;'>
                      <h5>Labels:</h5>
                      <div style='display: flex; align-items: center; gap: 10px; margin-bottom: 5px;'>
                        ${annotation.labels.map(label => `
                          <div style='width: 20px; height: 20px; background-color: ${label.backgroundColor}; margin-right: 4px;'></div>
                          <span style='font-weight: bold; margin-right: 10px;'>${label.text} (${Math.round(label.percentage)}%)</span>
                        `).join('')}
                      </div>
                      <div style='display: flex; width: 100%; height: 30px; border-radius: 4px; overflow: hidden;'>
                        ${annotation.labels.map(label => `
                          <div style='width: ${label.percentage}%; background-color: ${label.backgroundColor}; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 16px;'>
                            ${label.percentage > 10 ? label.text : ''}
                          </div>
                        `).join('')}
                      </div>
                    </div>
                  </div>
                `).join('')}
              </div>
            `).join('')}
          </div>
        `

        const opt = {
          margin: 1,
          filename: `all_versions_statistics_${this.currentProject.name}_${new Date().toISOString().split('T')[0]}.pdf`,
          image: { type: 'jpeg', quality: 0.98 },
          html2canvas: { scale: 2 },
          jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' }
        }

        await html2pdf().set(opt).from(element).save()
      } catch (error) {
        console.error('Error exporting PDF:', error)
        throw error
      }
    },

    exportToCSV() {
      // Cabeçalho
      const header = ['Version', 'Annotation Text', 'Labels', 'Discrepancy', 'Discrepancy Status']
      // Linhas
      const rows = this.annotationResults.flatMap(version => 
        version.annotations.map(annotation => {
          const labels = annotation.labels.map(l => `${l.text} (${Math.round(l.percentage)}%)`).join(', ')
          return [
            version.version_number,
            annotation.text.replace(/\n/g, ' '),
            labels,
            annotation.discrepancy ? 'Yes' : 'No',
            annotation.discrepancy ? (annotation.discrepancy_status || '') : ''
          ]
        })
      )
      // CSV string
      const csvContent = [header, ...rows]
        .map(row => row.map(field => '"' + String(field).replace(/"/g, '""') + '"').join(','))
        .join('\n')
      // Download
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      link.href = URL.createObjectURL(blob)
      link.setAttribute('download', `all_versions_statistics_${this.currentProject.name}_${new Date().toISOString().split('T')[0]}.csv`)
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    }
  }
})
</script>

<style scoped>
.v-card {
  margin: 8px 0;
}

.filter-select {
  width: 100%;
}

.filter-select ::v-deep .v-select__selections {
  max-height: 100px;
  overflow-y: auto;
}

.filter-select ::v-deep .v-select__selections input {
  width: 100%;
}

.label-stats {
  margin: 8px 0 0 0;
}

.label-bars {
  display: flex;
  width: 100%;
  height: 36px;
  border-radius: 4px;
  overflow: hidden;
}

.label-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  font-size: 14px;
  padding: 0 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>

 