<template>
  <form-create
    :name="editedItem.name"
    @update:name="editedItem.name = $event"
    @update:items="updateItems"
  >
    <template #default="{ valid }">
      <v-btn :disabled="!valid" color="primary" @click="save">
        Save
      </v-btn>
      <v-btn :disabled="!valid" color="primary" outlined @click="saveAndAnother">
        Save and add another
      </v-btn>
      <v-btn color="error" outlined @click="$router.back()">
        Cancel
      </v-btn>
    </template>
  </form-create>
</template>

<script lang="ts">
import Vue from 'vue'
import FormCreate from '~/components/perspective/FormCreate.vue'

interface PerspectiveItem {
  name: string;
  type: string;
  options: string;
}

interface EditedItem {
  name: string;
  items: PerspectiveItem[];
}

export default Vue.extend({
  components: {
    FormCreate
  },

  layout: 'project',

  middleware: ['check-auth', 'auth', 'setCurrentProject'],

  data() {
    return {
      editedItem: {
        name: '',
        items: []
      } as EditedItem,
      defaultItem: {
        name: '',
        items: []
      } as EditedItem
    }
  },

  computed: {
    projectId(): string {
      return this.$route.params.id
    },

    service(): any {
      return this.$services.perspective
    }
  },

  methods: {
    updateItems(items: PerspectiveItem[]) {
      this.editedItem.items = items;
    },

    async save() {
      try {
        await this.service.createPerspectiveWithItems(this.projectId, {
          name: this.editedItem.name,
          items: this.editedItem.items
        });

        this.$router.push(`/projects/${this.projectId}/perspective`);
      } catch (error: any) {
        if (error.response?.data?.error) {
          alert(error.response.data.error)
        } else {
          alert('Error creating perspective: ' + error)
        }
      }
    },

    async saveAndAnother() {
      try {
        await this.save();
        this.editedItem = Object.assign({}, this.defaultItem);
      } catch (error: any) {
        console.error('Error in saveAndAnother:', error);
      }
    }
  }
})
</script>