<template>
  <v-data-table
    :headers="headers"
    :items="items"
    :options.sync="options"
    :server-items-length="total"
    :loading="isLoading"
    :loading-text="$t('generic.loading')"
    :no-data-text="$t('vuetify.noDataAvailable')"
    :footer-props="{
      showFirstLastPage: true,
      'items-per-page-options': [10, 50, 100],
      'items-per-page-text': $t('vuetify.itemsPerPageText'),
      'page-text': $t('dataset.pageText')
    }"
    item-key="id"
    @input="$emit('input', $event)"
  >
    <template #[`item.text`]="{ item }">
      <span class="d-flex d-sm-none">{{ item.text.length > 50 ? item.text.substring(0, 50) + '...' : item.text }}</span>
      <span class="d-none d-sm-flex">{{ item.text.length > 200 ? item.text.substring(0, 200) + '...' : item.text }}</span>
    </template>
    <template #[`item.percentages`]="{ item }">
      <div>
        <v-chip
          v-for="(percentage, label) in item.percentages"
          :key="label"
          :color="getColor(percentage)"
          class="ma-1"
          small
        >
          {{ label }} ({{ percentage.toFixed(1) }}%)
        </v-chip>
      </div>
    </template>
    <template #[`item.status`]="{ item }">
      <v-chip :color="statusColor(item.status)" small>
        {{ item.status || 'Not Reported' }}
      </v-chip>
    </template>
    <template #[`item.actions`]="{ item }">
      <v-btn v-if="item.status === undefined || item.status === 'Not Reported'" small color="warning text-capitalize" @click="$emit('report', item)">
        Report
      </v-btn>
    </template>
  </v-data-table>
</template>

<script lang="ts">
import type { PropType } from 'vue'
import Vue from 'vue'
import { DataOptions } from 'vuetify/types'

export default Vue.extend({
  props: {
    isLoading: {
      type: Boolean,
      default: false,
      required: true
    },
    items: {
      type: Array as PropType<Array<{ id: number; text: string; percentages: Record<string, number>; status?: string }>>,
      default: () => [],
      required: true
    },
    total: {
      type: Number,
      default: 0,
      required: true
    }
  },

  data() {
    return {
      options: {} as DataOptions
    }
  },

  computed: {
    headers() {
      return [
        {
          text: this.$t('dataset.text'),
          value: 'text',
          sortable: false
        },
        {
          text: 'Percentages',
          value: 'percentages',
          sortable: false
        },
        {
          text: 'Status',
          value: 'status',
          sortable: false,
          width: '120px'
        },
        {
          text: 'Actions',
          value: 'actions',
          sortable: false,
          width: '100px'
        }
      ]
    }
  },

  watch: {
    options: {
      handler() {
        this.$emit('update:query', {
          query: {
            limit: this.options.itemsPerPage.toString(),
            offset: ((this.options.page - 1) * this.options.itemsPerPage).toString()
          }
        })
      },
      deep: true
    }
  },

  methods: {
    statusColor(status?: string) {
      if (status === 'Reported') return 'success'
      if (status === 'Not Reported' || status === undefined) return 'warning'
      if (status === 'solved') return 'success'
      if (status === 'unsolved') return 'error'
      return 'grey'
    },
    getColor(percentage: number): string {
      if (percentage >= 80) return 'success'
      if (percentage >= 50) return 'warning'
      return 'error'

    }
  }
})
</script>