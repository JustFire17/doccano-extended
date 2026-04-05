<template>
  <v-select
    :value="annotatedLabel"
    chips
    :items="labels"
    item-text="text"
    hide-details
    hide-selected
    return-object
    class="pt-0"
    @change="$emit('add', $event ? $event.id : null)"
  >
    <template #selection="{ attrs, item, select, selected }">
      <v-chip
        v-if="item.backgroundColor"
        v-bind="attrs"
        :input-value="selected"
        :color="item.backgroundColor"
        :text-color="$contrastColor(item.backgroundColor)"
        close
        @click="select"
        @click:close="$emit('add', null)"
      >
        <v-avatar v-if="item.suffixKey" left color="white" class="black--text font-weight-bold">
          {{ item.suffixKey }}
        </v-avatar>
        {{ item.text }}
      </v-chip>
    </template>
    <template #item="{ item }">
      <v-chip :color="item.backgroundColor" :text-color="$contrastColor(item.backgroundColor)">
        <v-avatar v-if="item.suffixKey" left color="white" class="black--text font-weight-bold">
          {{ item.suffixKey }}
        </v-avatar>
        {{ item.text }}
      </v-chip>
    </template>
  </v-select>
</template>

<script>
export default {
  props: {
    labels: {
      type: Array,
      default: () => [],
      required: true
    },
    annotations: {
      type: Array,
      default: () => [],
      required: true
    }
  },

  computed: {
    annotatedLabel() {
      const labelIds = this.annotations.map((item) => item.label)
      return this.labels.find((item) => labelIds.includes(item.id))
    }
  }
}
</script>
