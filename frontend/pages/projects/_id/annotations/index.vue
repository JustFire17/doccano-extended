<template>
  <v-card>
    <v-card-title class="headline">
      <v-icon left>mdi-note-text</v-icon>
      Annotations
    </v-card-title>

    <!-- Filtros -->
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

                <!-- Perspective filter -->
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

                <!-- Perspective value filter -->
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

                <!-- Labels filter -->
                <v-select
                  v-model="filters.labelIds"
                  :items="availableLabels"
                  item-text="text"
                  item-value="id"
                  label="Filter by Labels"
                  multiple
                  chips
                  clearable
                  @change="applyFilters"
                />

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
              </v-form>
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12" md="9">
          <!-- Tabela de Anotações -->
          <v-data-table
            :headers="headers"
            :items="annotations"
            :options.sync="options"
            :server-items-length="total"
            :loading="isLoading"
            :loading-text="$t('generic.loading')"
            :no-data-text="noDataMessage"
            :footer-props="{
              showFirstLastPage: true,
              'items-per-page-options': [10, 25, 50, 100],
              'items-per-page-text': $t('vuetify.itemsPerPageText'),
              'page-text': $t('dataset.pageText')
            }"
            item-key="id"
            class="elevation-1"
          >
            <!-- Slot para o texto do exemplo -->
            <template #[`item.text`]="{ item }">
              <div class="text-truncate" style="max-width: 300px;" :title="item.text">
                {{ item.text }}
              </div>
            </template>

            <!-- Slot para as labels -->
            <template #[`item.labels`]="{ item }">
              <div class="d-flex flex-wrap">
                <v-chip
                  v-for="label in item.labels"
                  :key="label.id"
                  :color="label.backgroundColor"
                  text-color="white"
                  small
                  class="ma-1"
                >
                  {{ label.text }}
                </v-chip>
              </div>
            </template>

            <!-- Slot para a versão -->
            <template #[`item.version`]="{ item }">
              <v-chip
                v-if="item.version"
                color="blue"
                text-color="white"
                small
              >
                v{{ item.version }}
              </v-chip>
              <span v-else class="grey--text">N/A</span>
            </template>

            <!-- Slot para os usuários -->
            <template #[`item.users`]="{ item }">
              <div v-if="item.users && item.users.length > 0" class="d-flex flex-wrap">
                <v-chip
                  v-for="user in item.users"
                  :key="user.id"
                  color="green"
                  text-color="white"
                  small
                  class="ma-1"
                >
                  {{ user.username }}
                </v-chip>
              </div>
              <span v-else class="grey--text">No annotators</span>
            </template>

            <!-- Slot para a data de criação -->
            <template #[`item.created_at`]="{ item }">
              <span v-if="item.created_at">
                {{ formatDate(item.created_at) }}
              </span>
              <span v-else class="grey--text">N/A</span>
            </template>

            <!-- Slot para ações -->
            <template #[`item.actions`]="{ item }">
              <v-btn
                color="primary"
                text
                small
                @click="viewAnnotation(item)"
              >
                <v-icon small>mdi-eye</v-icon>
                View
              </v-btn>
              <v-btn
                v-if="project.closed && item.version === project.version"
                color="warning"
                text
                small
                @click="openDiscrepancyDialog(item)"
              >
                <v-icon small>mdi-alert-circle</v-icon>
                Report
              </v-btn>
            </template>
          </v-data-table>

          <!-- Dialog para visualizar anotação -->
          <v-dialog v-model="viewDialog" max-width="800px">
            <v-card>
              <v-card-title class="headline">
                <v-icon left>mdi-note-text</v-icon>
                Annotation Details
              </v-card-title>
              <v-card-text>
                <v-container>
                  <v-row>
                    <v-col cols="12">
                      <v-text-field
                        label="Example ID"
                        :value="selectedAnnotation.example_id"
                        readonly
                      />
                    </v-col>
                    <v-col cols="12">
                      <v-text-field
                        label="Version"
                        :value="'v' + selectedAnnotation.version"
                        readonly
                      />
                    </v-col>
                    <v-col cols="12">
                      <v-textarea
                        label="Text"
                        :value="selectedAnnotation.text"
                        readonly
                        rows="4"
                      />
                    </v-col>
                    <v-col cols="12">
                      <v-text-field
                        label="Created At"
                        :value="formatDate(selectedAnnotation.created_at)"
                        readonly
                      />
                    </v-col>
                    <v-col cols="12">
                      <v-subheader>Labels</v-subheader>
                      <div class="d-flex flex-wrap">
                        <v-chip
                          v-for="label in selectedAnnotation.labels"
                          :key="label.id"
                          :color="label.backgroundColor"
                          text-color="white"
                          class="ma-1"
                        >
                          {{ label.text }} ({{ label.percentage.toFixed(1) }}%)
                        </v-chip>
                      </div>
                    </v-col>
                    <v-col cols="12">
                      <v-subheader>Annotators</v-subheader>
                      <div v-if="selectedAnnotation.users && selectedAnnotation.users.length > 0" class="d-flex flex-wrap">
                        <v-chip
                          v-for="user in selectedAnnotation.users"
                          :key="user.id"
                          color="green"
                          text-color="white"
                          class="ma-1"
                        >
                          {{ user.username }}
                        </v-chip>
                      </div>
                      <span v-else class="grey--text">No annotators</span>
                    </v-col>
                  </v-row>
                </v-container>
              </v-card-text>
              <v-card-actions>
                <v-spacer />
                <v-btn color="primary" text @click="viewDialog = false">
                  Close
                </v-btn>
              </v-card-actions>
            </v-card>
          </v-dialog>

          <!-- Dialog para reportar discrepância -->
          <manual-discrepancy-dialog
            v-model="showManualDiscrepancyDialog"
            :example="selectedExampleForDiscrepancy"
          />
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script>
import { mdiMagnify, mdiCalendar, mdiNoteText } from '@mdi/js';
import { mapGetters } from 'vuex';
import ManualDiscrepancyDialog from '@/components/discrepancies/ManualDiscrepancyDialog.vue';

export default {
  components: {
    ManualDiscrepancyDialog
  },
  layout: "project",
  middleware: ["check-auth", "auth"],
  
  data() {
    return {
      mdiMagnify,
      mdiCalendar,
      mdiNoteText,
      search: "",
      selectedLabels: [],
      selectedUsers: [],
      startDate: null,
      endDate: null,
      startDateMenu: false,
      endDateMenu: false,
      annotations: [],
      availableLabels: [],
      availableUsers: [],
      total: 0,
      isLoading: false,
      viewDialog: false,
      selectedAnnotation: {},
      options: {},
      headers: [
        { text: "Text", value: "text", sortable: false },
        { text: "Labels", value: "labels", sortable: false },
        { text: "Version", value: "version", sortable: true },
        { text: "Annotators", value: "users", sortable: false },
        { text: "Created At", value: "created_at", sortable: true },
        { text: "Actions", value: "actions", sortable: false }
      ],
      datePickerStart: false,
      datePickerEnd: false,
      startDateText: 'All time',
      endDateText: 'Present',
      filters: {
        dateStart: null,
        dateEnd: null,
        labelIds: [],
        username: [],
        perspectiveId: [],
        exampleId: [],
        projectVersion: []
      },
      perspectives: [],
      selectedPerspectiveValues: [],
      allPerspectiveValues: [],
      perspectiveValuesMap: {},
      userOptions: [],
      exampleOptions: [],
      versionOptions: [],
      showManualDiscrepancyDialog: false,
      selectedExampleForDiscrepancy: null,
      error: null
    };
  },

  computed: {
    ...mapGetters('projects', ['project']),
    
    projectId() {
      return this.$route.params.id;
    },
    
    noDataMessage() {
      // Check if any filters are applied
      const hasFilters = 
        this.filters.dateStart ||
        this.filters.dateEnd ||
        (this.filters.labelIds && this.filters.labelIds.length > 0) ||
        (this.filters.username && this.filters.username.length > 0) ||
        (this.filters.perspectiveId && this.filters.perspectiveId.length > 0) ||
        (this.selectedPerspectiveValues && this.selectedPerspectiveValues.length > 0) ||
        (this.filters.exampleId && this.filters.exampleId.length > 0) ||
        (this.filters.projectVersion && this.filters.projectVersion.length > 0);
        
      if (hasFilters) {
        const appliedFilters = [];
        
        if (this.filters.dateStart || this.filters.dateEnd) {
          appliedFilters.push('date range');
        }
        if (this.filters.labelIds && this.filters.labelIds.length > 0) {
          appliedFilters.push(`${this.filters.labelIds.length} label(s)`);
        }
        if (this.filters.username && this.filters.username.length > 0) {
          appliedFilters.push(`${this.filters.username.length} user(s)`);
        }
        if (this.filters.perspectiveId && this.filters.perspectiveId.length > 0) {
          appliedFilters.push('perspective');
        }
        if (this.filters.exampleId && this.filters.exampleId.length > 0) {
          appliedFilters.push(`${this.filters.exampleId.length} example(s)`);
        }
        if (this.filters.projectVersion && this.filters.projectVersion.length > 0) {
          appliedFilters.push(`${this.filters.projectVersion.length} version(s)`);
        }
        
        const filterText = appliedFilters.join(', ');
        return `No annotations found matching the applied filters (${filterText}). Try adjusting your filter criteria or clearing some filters.`;
      } else {
        return "No annotations available";
      }
    }
  },

  watch: {
    options: {
      handler() {
        this.fetchAnnotations();
      },
      deep: true
    }
  },

  mounted() {
    this.loadPerspectives();
    this.loadFilterOptions();
    this.fetchAnnotations();
  },

  methods: {
    async loadPerspectives() {
      try {
        this.perspectives = [];
        const project = await this.$services.project.findById(this.projectId);
        
        if (project && project.perspective_associated) {
          const perspectives = await this.$services.perspective.list(this.projectId);
          if (perspectives && Array.isArray(perspectives)) {
            this.perspectives = perspectives;
          }
        }
      } catch (error) {
        console.error('Error loading perspectives:', error);
        this.perspectives = [];
      }
    },

    async loadFilterOptions() {
      try {
        const projectId = this.$route.params.id;
        
        // Load all annotations without filters to populate filter options
        const response = await this.$services.annotation.getAnnotations(projectId, {});
        
        this.populateFilterOptions(response.annotations);
      } catch (error) {
        console.error("Error loading filter options:", error);
      }
    },

    async onPerspectiveChange() {
      this.selectedPerspectiveValues = []
      this.allPerspectiveValues = []
      this.perspectiveValuesMap = {}
      this.error = null

      if (this.filters.perspectiveId && this.filters.perspectiveId.length > 0) {
        try {
          const allValues = await this.$services.perspective.getAllFilledValues(this.projectId)
      
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
      this.applyFilters()
    },

    async fetchAnnotations() {
      this.isLoading = true
      try {
        const filters = {
          dateStart: this.filters.dateStart,
          dateEnd: this.filters.dateEnd,
          labelTexts: this.filters.labelIds.length > 0 ? this.filters.labelIds : undefined,
          userIds: this.filters.username.length > 0 ? this.filters.username : undefined,
          perspectiveIds: this.filters.perspectiveId.length > 0 ? this.filters.perspectiveId : undefined,
          perspectiveValues: this.selectedPerspectiveValues.length > 0 ? this.selectedPerspectiveValues : undefined,
          annotationIds: this.filters.exampleId.length > 0 ? this.filters.exampleId : undefined,
          projectVersion: this.filters.projectVersion.length > 0 ? this.filters.projectVersion : undefined
        }

        const response = await this.$services.annotation.getAnnotations(this.projectId, filters)
        this.annotations = response.annotations
        this.total = response.total || response.annotations.length
      } catch (error) {
        console.error('Error fetching annotations:', error)
        this.error = 'Error fetching annotations. Please try again.'
      } finally {
        this.isLoading = false
      }
    },

    populateFilterOptions(annotations) {
      if (!annotations || !Array.isArray(annotations)) {
        return;
      }

      // Populate user options
      const uniqueUsers = [...new Set(annotations.flatMap(item => 
        (item.users && Array.isArray(item.users)) ? item.users.map(user => user.username) : []
      ))];
      this.userOptions = uniqueUsers.filter(username => username).sort();

      // Populate example options
      const examples = new Map();
      annotations.forEach(item => {
        if (item.example_id && item.text && !examples.has(item.example_id)) {
          const shortText = item.text.length > 50 
            ? item.text.substring(0, 50) + '...' 
            : item.text;
          examples.set(item.example_id, {
            text: item.text,
            display_text: shortText,
            id: item.example_id
          });
        }
      });
      this.exampleOptions = Array.from(examples.values())
        .sort((a, b) => a.display_text.localeCompare(b.display_text));

      // Populate label options - group by text to avoid duplicates across versions
      const labels = new Map();
      annotations.forEach(item => {
        if (item.labels && Array.isArray(item.labels)) {
          item.labels.forEach(label => {
            if (label.text && !labels.has(label.text)) {
              labels.set(label.text, {
                id: label.text, // Use text as ID for the filter
                text: label.text,
                backgroundColor: label.backgroundColor || '#757575'
              });
            }
          });
        }
      });
      this.availableLabels = Array.from(labels.values())
        .sort((a, b) => a.text.localeCompare(b.text));

      // Populate version options
      const versions = [...new Set(annotations.map(item => item.version).filter(v => v !== null && v !== undefined))];
      this.versionOptions = versions.map(v => ({
        text: `Version ${v}`,
        value: v
      })).sort((a, b) => a.value - b.value);
    },

    viewAnnotation(annotation) {
      this.selectedAnnotation = annotation;
      this.viewDialog = true;
    },

    formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    },

    updateStartDate() {
      if (this.filters.dateStart) {
        this.startDateText = this.formatDateForDisplay(this.filters.dateStart);
      } else {
        this.startDateText = 'All time';
      }
      this.datePickerStart = false;
      this.applyFilters();
    },

    clearStartDate() {
      this.filters.dateStart = null;
      this.startDateText = 'All time';
      this.applyFilters();
    },

    updateEndDate() {
      if (this.filters.dateEnd) {
        this.endDateText = this.formatDateForDisplay(this.filters.dateEnd);
      } else {
        this.endDateText = 'Present';
      }
      this.datePickerEnd = false;
      this.applyFilters();
    },

    clearEndDate() {
      this.filters.dateEnd = null;
      this.endDateText = 'Present';
      this.applyFilters();
    },

    formatDateForDisplay(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleDateString();
    },

    applyFilters() {
      this.fetchAnnotations();
    },

    openDiscrepancyDialog(item) {
      // Criar um objeto exemplo baseado no item da annotation
      this.selectedExampleForDiscrepancy = {
        id: item.example_id,
        text: item.text,
        isConfirmed: true // Assumir que está confirmado já que estamos numa página de annotations
      };
      this.showManualDiscrepancyDialog = true;
    }
  }
};
</script>

<style scoped>
.text-truncate {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style> 