<template>
  <v-container>
    <v-card v-if="!isLoading && discrepancyPercentage !== null" class="mb-4">
      <v-card-text>
        <v-row align="center">
          <v-col cols="12" sm="6">
            <p class="text-h6">Discrepancy Threshold:</p>
          </v-col>
          <v-col cols="12" sm="6" class="text-right">
            <p class="text-h5 font-weight-bold">{{ discrepancyPercentage }}%</p>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <v-alert v-if="isLoading" type="info" border="left" prominent>
      Loading discrepancies, please wait...
    </v-alert>
    <v-alert v-if="error" type="error" border="left" prominent>
      {{ error }}
    </v-alert>

    <v-row class="mb-4">
      <!-- Text filter -->
      <v-col cols="12" md="6">
        <v-select
          v-model="filters.textIds"
          :items="textOptions"
          label="Filter by Text"
          item-text="display_text"
          item-value="id"
          multiple
          chips
          clearable
          @change="applyFilters"
        ></v-select>
      </v-col>

      <!-- Labels filter -->
      <v-col cols="12" md="6">
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
      </v-col>
    </v-row>

    <DiscrepanciesList
      v-if="!isLoading && !error"
      :items="filteredDiscrepancies"
      :is-loading="isLoading"
      :total="filteredTotal"
      @update:query="onQueryUpdate"
      @report="openDiscrepancyDialog"
    />

    <automatic-discrepancy-dialog
      v-model="showManualDiscrepancyDialog"
      :example="selectedExample"
    />
  </v-container>
</template>

<script>
import DiscrepanciesList from '~/components/discrepancies/DiscrepanciesList.vue'
import AutomaticDiscrepancyDialog from '~/components/discrepancies/AutomaticDiscrepancyDialog.vue'

export default {
  components: {
    DiscrepanciesList,
    AutomaticDiscrepancyDialog
  },

  layout: "project",
  middleware: ["check-auth", "auth"],
  data() {
    return {
      discrepancyPercentage: null,
      discrepancies: [],
      isLoading: false,
      error: null,
      total: 0,
      query: { limit: 10, offset: 0 },
      showManualDiscrepancyDialog: false,
      selectedExample: null,
      filters: {
        textIds: [],
        labelIds: []
      },
      textOptions: [],
      availableLabels: []
    };
  },
  computed: {
    filteredDiscrepancies() {
      let filtered = this.discrepancies;

      // Filter by text
      if (this.filters.textIds && this.filters.textIds.length > 0) {
        filtered = filtered.filter(item => this.filters.textIds.includes(item.id));
      }

      // Filter by labels
      if (this.filters.labelIds && this.filters.labelIds.length > 0) {
        filtered = filtered.filter(item => {
          const itemLabels = Object.keys(item.percentages);
          return this.filters.labelIds.some(labelId => itemLabels.includes(labelId));
        });
      }

      // Sort by discrepancy level (lowest max percentage first = highest discrepancy first)
      filtered.sort((a, b) => {
        const maxPercentageA = Math.max(...Object.values(a.percentages));
        const maxPercentageB = Math.max(...Object.values(b.percentages));
        return maxPercentageA - maxPercentageB; // Ascending order: less consensus first
      });

      return filtered;
    },
    
    filteredTotal() {
      return this.filteredDiscrepancies.length;
    }
  },

  mounted() {
    this.fetchDiscrepancyData();
    this.fetchDiscrepancies(this.query);
  },
  methods: {
    async fetchDiscrepancyData() {
      try {
        const projectId = this.$route.params.id;
        const response = await this.$axios.get(`/v1/projects/${projectId}`);
        this.discrepancyPercentage = response.data.discrepancy_percentage;
      } catch (error) {
        console.error("Error fetching discrepancy data:", error.response?.data);
        if (error.response && error.response.status === 500) {
          this.error = "Database unavailable. Please try again later.";
        } else {
          this.error = "Failed to load project data. Please try again later.";
        }
      }
    },
    async fetchDiscrepancies(query) {
      this.isLoading = true;
      try {
        const projectId = this.$route.params.id;
        const response = await this.$axios.get(`/v1/projects/${projectId}/discrepancies`, {
          params: query,
        });
        this.discrepancies = response.data.discrepancies;
        this.total = response.data.discrepancies.length;
        
        // Populate filter options
        this.populateFilterOptions(this.discrepancies);
      } catch (error) {
        console.error("Error fetching discrepancies:", error.response?.data);
        if (error.response && error.response.status === 500) {
          this.error = "The database is currently unavailable. Please try again later.";
        } else if (error.response && error.response.status === 404) {
          this.error = "No discrepancies found for this project.";
        } else {
          this.error = "Failed to load discrepancies. Please check your connection or contact support.";
        }
      } finally {
        this.isLoading = false;
      }
    },

    populateFilterOptions(discrepancies) {
      // Populate text options
      const texts = new Map();
      discrepancies.forEach(item => {
        if (!texts.has(item.id)) {
          const shortText = item.text.length > 50 
            ? item.text.substring(0, 50) + '...' 
            : item.text;
          texts.set(item.id, {
            text: item.text,
            display_text: shortText,
            id: item.id
          });
        }
      });
      this.textOptions = Array.from(texts.values())
        .sort((a, b) => a.display_text.localeCompare(b.display_text));

      // Populate label options
      const labels = new Map();
      discrepancies.forEach(item => {
        Object.keys(item.percentages).forEach(labelText => {
          if (!labels.has(labelText)) {
            labels.set(labelText, {
              id: labelText, // Use text as ID for the filter
              text: labelText
            });
          }
        });
      });
      this.availableLabels = Array.from(labels.values())
        .sort((a, b) => a.text.localeCompare(b.text));
    },

    applyFilters() {
      // Triggers the computed property to update
      this.$forceUpdate();
    },
    onQueryUpdate(newQuery) {
      if (JSON.stringify(this.query) !== JSON.stringify(newQuery)) {
        this.query = newQuery;
        this.fetchDiscrepancies(this.query);
      }
    },
    openDiscrepancyDialog(item) {
      this.selectedExample = {
        id: item.id,
        text: item.text
      }
      this.showManualDiscrepancyDialog = true
    }
  },
};
</script>

<style scoped>
.text-h4 {
  color: #3f51b5;
}

.text-h5 {
  color: #1e88e5;
}

.text-subtitle-1 {
  color: #757575;
}

.error-message {
  color: red;
  font-weight: bold;
}
</style>