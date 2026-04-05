<template>
  <div>
    <v-card>
      <v-card-title>
        <span class="headline">Label Table per Annotation</span>
        <v-spacer></v-spacer>
        <v-btn color="primary" :loading="loading" @click="applyFilters">
          Show Statistics
        </v-btn>
        <v-btn color="primary" type="button" @click="openExportDialog">
          Export
        </v-btn>
      </v-card-title>
      <v-card-text>
        <v-row>
          <v-col cols="12" md="4">
            <v-autocomplete
              v-model="selectedTexts"
              :items="allTexts"
              label="Filter by Annotation Text"
              multiple
              chips
              clearable
              :menu-props="{ maxHeight: '400px' }"
              class="filter-select"
            />
          </v-col>
          <v-col cols="12" md="4">
            <v-autocomplete
              v-model="selectedLabels"
              :items="labels"
              label="Filter by Label"
              multiple
              chips
              clearable
              :menu-props="{ maxHeight: '400px' }"
              class="filter-select"
            />
          </v-col>
          <v-col cols="12" md="4">
            <v-autocomplete
              v-model="selectedPerspectives"
              :items="perspectives"
              item-text="name"
              item-value="id"
              label="Filter by Perspective"
              multiple
              chips
              clearable
              :menu-props="{ maxHeight: '400px' }"
              class="filter-select"
              @change="onPerspectiveChange"
            />
          </v-col>
          <v-col v-if="selectedPerspectives.length > 0" cols="12" md="4">
            <v-autocomplete
              v-model="selectedPerspectiveValues"
              :items="allPerspectiveValues"
              label="Filter by Perspective Value"
              multiple
              chips
              clearable
              :menu-props="{ maxHeight: '400px' }"
              class="filter-select"
            />
          </v-col>
        </v-row>
        <v-data-table
          :headers="tableHeaders"
          :items="filteredRows"
          :loading="loading"
          class="elevation-1"
          :items-per-page="20"
          :no-data-text="'There are no records to display.'"
        >
          <template #[`item.text`]="{ item }">
            <div class="text-truncate" style="max-width: 350px;" :title="item.text">
              {{ item.text }}
            </div>
          </template>
          <template v-for="label in labels" #[`item.labels.${label}`]="{ item }">
            <div :key="label" class="text-center">
              {{ item.labels[label] }}
            </div>
          </template>
          <template #[`item.discrepancy`]="{ item }">
            <v-chip v-if="item.discrepancy" color="error" small>Discrepancy</v-chip>
            <v-chip v-else color="success" small>No Discrepancy</v-chip>
          </template>
          <template #[`item.reported`]="{ item }">
            <v-chip v-if="item.reported" color="success" small>Reported</v-chip>
            <v-chip v-else color="grey" small>Not Reported</v-chip>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>

    <v-dialog v-model="exportDialog" max-width="400px">
      <v-card>
        <v-card-title class="headline">Export Options</v-card-title>
        <v-card-text>
          <v-checkbox v-model="exportFormats" label="PDF" value="pdf" hide-details />
          <v-checkbox v-model="exportFormats" label="CSV" value="csv" hide-details />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn color="red" text @click="closeExportDialog">Cancel</v-btn>
          <v-btn color="primary" text @click="exportData">Export</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script lang="ts">
import Vue from 'vue'
import { mapGetters } from 'vuex'
import html2pdf from 'html2pdf.js'

export default Vue.extend({
  layout: 'project',
  middleware: ['check-auth', 'auth', 'setCurrentProject'],
  data() {
    return {
      loading: false,
      exportDialog: false,
      exportFormats: ['pdf', 'csv'] as string[],
      labels: [] as string[],
      rows: [] as any[],
      filteredRows: [] as any[],
      allTexts: [] as string[],
      selectedTexts: [] as string[],
      selectedLabels: [] as string[],
      perspectives: [] as any[],
      selectedPerspectives: [] as any[],
      allPerspectiveValues: [] as string[],
      selectedPerspectiveValues: [] as string[],
      perspectiveValuesMap: {} as Record<string, string[]>
    }
  },
  computed: {
    ...mapGetters('projects', ['project']),
    projectId(): string {
      return this.$route.params.id
    },
    tableHeaders(): any[] {
      const base = [
        { text: 'Annotation Text', value: 'text', align: 'start', sortable: false }
      ]
      base.push(...this.labels.map(label => ({ text: label, value: `labels.${label}`, align: 'center', sortable: false })))
      base.push(
        { text: 'Discrepancy', value: 'discrepancy', align: 'center', sortable: false },
        { text: 'Reported', value: 'reported', align: 'center', sortable: false }
      )
      return base
    }
  },
  async created() {
    await this.loadTable()
    await this.loadPerspectives()
    this.filteredRows = []
  },
  methods: {
    async loadTable() {
      this.loading = true
      try {
        const response = await this.$services.project.getAnnotationLabelTable(this.projectId)
        this.labels = response.labels
        this.rows = response.rows
        this.allTexts = response.rows.map((r: any) => r.text)
      } catch (error) {
        this.labels = []
        this.rows = []
        this.allTexts = []
        this.filteredRows = []
        alert("Sorry, we couldn't load label table right now. Please try again in a few moments.")
      } finally {
        this.loading = false
      }
    },
    async loadPerspectives() {
      try {
        this.perspectives = await this.$services.perspective.list(this.projectId)
      } catch (error) {
        this.perspectives = []
      }
    },
    async onPerspectiveChange() {
      this.selectedPerspectiveValues = []
      this.allPerspectiveValues = []
      this.perspectiveValuesMap = {}
      console.log('selectedPerspectives:', this.selectedPerspectives)
      const allValues: Record<string, string[]> = await this.$services.perspective.getAllFilledValues(this.projectId)
      console.log('allValues do backend:', allValues)
      if (this.selectedPerspectives && this.selectedPerspectives.length > 0) {
        try {
          this.selectedPerspectives.forEach((persp: number) => {
            const perspectiveId = String(persp)
            if (allValues[perspectiveId]) {
              this.perspectiveValuesMap[perspectiveId] = allValues[perspectiveId]
              allValues[perspectiveId].forEach((value: string) => {
                if (!this.allPerspectiveValues.includes(value)) {
                  this.allPerspectiveValues.push(value)
                }
              })
            }
          })
          this.allPerspectiveValues = [...this.allPerspectiveValues]
        } catch (error) {
          this.allPerspectiveValues = []
        }
      }
      console.log('Valores possíveis:', this.allPerspectiveValues)
    },
    applyFilters() {
      if (
        this.selectedTexts.length === 0 &&
        this.selectedLabels.length === 0 &&
        this.selectedPerspectives.length === 0 &&
        this.selectedPerspectiveValues.length === 0
      ) {
        this.filteredRows = this.rows
        return
      }
      let filtered = this.rows
      if (this.selectedTexts.length > 0) {
        filtered = filtered.filter(row => this.selectedTexts.includes(row.text))
      }
      if (this.selectedLabels.length > 0) {
        filtered = filtered.filter(row => this.selectedLabels.some(label => row.labels[label] > 0))
      }
      if (this.selectedPerspectives.length > 0 && this.selectedPerspectiveValues.length > 0) {
        filtered = filtered.filter(row => {
          console.log('row.perspectives:', row.perspectives)
          return this.selectedPerspectives.every((persp: number) => {
            const value = row.perspectives ? row.perspectives[String(persp)] : undefined
            console.log('Comparar:', value, this.selectedPerspectiveValues)
            return value && this.selectedPerspectiveValues.includes(value)
          })
        })
      }
      this.filteredRows = filtered
    },
    openExportDialog() {
      this.exportDialog = true
    },
    closeExportDialog() {
      this.exportDialog = false
    },
    async exportData() {
      if (!this.exportFormats.length) {
        alert('Please select at least one export format.')
        return
      }

      if (this.exportFormats.includes('csv')) {
        this.exportToCSV()
      }
      if (this.exportFormats.includes('pdf')) {
        await this.exportToPDF()
      }

      this.closeExportDialog()
    },
    exportToCSV() {
      const header = ['Annotation Text', ...this.labels, 'Discrepancy', 'Reported']
      const rows = this.filteredRows.map((row: any) => {
        const labelCounts = this.labels.map(label => row.labels[label])
        return [row.text, ...labelCounts, row.discrepancy ? 'Yes' : 'No', row.reported ? 'Yes' : 'No']
      })
      const csvContent = [header, ...rows]
        .map((r) => (r as string[]).map(f => '"' + String(f).replace(/"/g, '""') + '"').join(','))
        .join('\n')
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      link.href = URL.createObjectURL(blob)
      link.setAttribute('download', `label_table_per_annotation_${new Date().toISOString().split('T')[0]}.csv`)
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    },
    async exportToPDF() {
      // Cria um PDF simples com os dados filtrados
      const element = document.createElement('div')
      element.innerHTML = `
        <h1>Label Table per Annotation</h1>
        <div style='margin-bottom: 40px;'>Exported on: ${new Date().toLocaleString()}</div>
        <table border='1' cellpadding='6' cellspacing='0' style='border-collapse: collapse; width: 100%;'>
          <thead>
            <tr>
              <th>Annotation Text</th>
              ${this.labels.map(label => `<th>${label}</th>`).join('')}
              <th>Discrepancy</th>
              <th>Reported</th>
            </tr>
          </thead>
          <tbody>
            ${this.filteredRows.map(row => `
              <tr>
                <td>${row.text}</td>
                ${this.labels.map(label => `<td>${row.labels[label]}</td>`).join('')}
                <td>${row.discrepancy ? 'Yes' : 'No'}</td>
                <td>${row.reported ? 'Yes' : 'No'}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      `
      const opt = {
        margin: 1,
        filename: `label_table_per_annotation_${new Date().toISOString().split('T')[0]}.pdf`,
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2 },
        jsPDF: { unit: 'in', format: 'letter', orientation: 'landscape' }
      }
      await html2pdf().set(opt).from(element).save()
    }
  }
})
</script>

<style scoped>
.text-truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style> 