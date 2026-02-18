<template>
  <v-container class="pt-16">
    <!-- Botão de Criação -->
    <v-btn class="text-capitalize mt-4 d-flex justify-end" color="primary" @click="openCreateDialog">
      {{ $t("generic.create") }}
    </v-btn>

    <!-- Tabela de Grupos -->
    <v-data-table :value="groups" :headers="headers" :items="groups" :options.sync="options"
      :server-items-length="total" :search="search" :loading="isLoading" :loading-text="$t('generic.loading')"
      :no-data-text="$t('There is no groups listed at the moment')" :footer-props="{
        showFirstLastPage: true,
        'items-per-page-options': [10, 50, 100],
        'items-per-page-text': $t('vuetify.itemsPerPageText'),
        'page-text': $t('dataset.pageText')
      }" item-key="id" show-select>

      <template #top>
        <v-text-field v-model="search" :prepend-inner-icon="mdiMagnify" :label="$t('generic.search')" single-line
          hide-details filled />
      </template>

      <!-- Ações (Editar/Excluir) -->
      <template #[`item.actions`]="{ item }">
        <v-btn color="primary" text @click="openEditDialog(item)">{{ $t("generic.edit") }}</v-btn>
        <v-btn color="red" text @click="deleteGroup(item.id)">{{ $t("generic.delete") }}</v-btn>
      </template>
    </v-data-table>

    <!-- Diálogo de Criação -->
    <v-dialog v-model="createDialog" max-width="600px">
      <v-card>
        <v-card-title>Create Group</v-card-title>
        <v-card-text>
          <v-form ref="createForm">
            <v-text-field v-model="createForm.name" label="Group Name" required />
            <v-combobox v-model="createForm.selectedPermissions" :items="allPermissions" item-text="description"
              item-value="id" label="Permissions" multiple chips />
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn color="red" text @click="createDialog = false">Cancel</v-btn>
          <v-btn color="primary" @click="createGroup">Create</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Diálogo de Edição -->
    <v-dialog v-model="editDialog" max-width="600px">
      <v-card>
        <v-card-title>Edit Group</v-card-title>
        <v-card-text>
          <v-form ref="editForm">
            <v-text-field v-model="editForm.name" label="Group Name" required />
            <v-combobox v-model="editForm.selectedPermissions" :items="allPermissions" item-text="description"
              item-value="id" label="Permissions" multiple chips />
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn color="red" text @click="editDialog = false">Cancel</v-btn>
          <v-btn color="primary" @click="editGroup">Save</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script>
export default {
  layout: "projects",
  middleware: ["check-auth", "auth"],
  data() {
    return {
      search: "",
      groups: [],
      allPermissions: [],
      createDialog: false,
      editDialog: false,
      createForm: {
        name: '',
        selectedPermissions: []
      },
      editForm: {
        id: null,
        name: '',
        selectedPermissions: []
      },
      headers: [
        { text: 'Name', value: 'name' },
        { text: 'Permissions', value: 'permissions.length' },
        { text: 'Actions', value: 'actions' }
      ]
    };
  },
  mounted() {
      this.isAdminUserCheck()
      this.fetchGroups();
      this.fetchPermissions();
    
  },
  methods: {
    async fetchGroups() {
      try {
        const response = await this.$axios.get('/v1/groups');
        this.groups = response.data;
      } catch (error) {
        console.error('Error fetching groups:', error);
        let message = "Sorry, we couldn't load the groups right now. Please try again in a few moments.";
        if (error.response?.data?.detail) {
          message = error.response.data.detail;
        }
        alert(message);
      }
    },
    async fetchPermissions() {
      try {
        const response = await this.$axios.get('/v1/groups/permissions/?limit=225');
        this.allPermissions = response.data.results.map(permission => ({
          ...permission,
          description: permission.description || `${permission.content_type} | ${permission.codename} | ${permission.name}`
        }));
      } catch (error) {
        console.error('Error fetching permissions:', error);
      }
    },
    async isAdminUserCheck(){
      if (!this.$store.getters['auth/isAuthenticated']) {
        alert("You must be logged in to access this page!");
        this.$router.push('/auth');
        return;
      }
      const response = await this.$axios.get("/v1/me");
      const user = response.data;
      console.log("User:", user);
      if (!user.is_superuser) {
        alert("You don't have permission to access this page!");
        this.$router.push("/");
      }
    },
    openCreateDialog() {
      this.createForm = { name: '', selectedPermissions: [] };
      this.createDialog = true;
    },
    openEditDialog(group) {
      this.editForm = {
        id: group.id,
        name: group.name,
        selectedPermissions: group.permissions.map(permissionId => {
          return this.allPermissions.find(permission => permission.id === permissionId) || { id: permissionId };
        })
      };
      this.editDialog = true;
    },
    async createGroup() {
      try {
        const groupData = {
          name: this.createForm.name,
          permission_ids: this.createForm.selectedPermissions.map(p => p.id || p),
        };
        console.log("Creating group with data:", groupData);
        await this.$axios.post("/v1/groups/create", groupData);
        alert("Group created successfully!");
        this.fetchGroups();
        this.createDialog = false;
      } catch (error) {
        console.error("Error creating group:", error.response?.data);
        let message = "Sorry, we couldn't create the group right now. Please try again in a few moments.";
        if (error.response?.data?.detail) {
          message = error.response.data.detail;
        }
        alert(message);
      }
    },
    async editGroup() {
      try {
        const groupData = {
          name: this.editForm.name,
          permission_ids: this.editForm.selectedPermissions.map(p => p.id || p),
        };
        console.log("Editing group with data:", groupData);
        await this.$axios.put(`/v1/groups/update/${this.editForm.id}/`, groupData);
        alert("Group updated successfully!");
        this.fetchGroups();
        this.editDialog = false;
      } catch (error) {
        console.error("Error editing group:", error.response?.data || error.message);
        let message = "Sorry, we couldn't update the group right now. Please try again in a few moments.";
        if (error.response?.data?.detail) {
          message = error.response.data.detail;
        }
        alert(message);
      }
    },
    async deleteGroup(groupId) {
      if (confirm('Are you sure you want to delete this Group?')) {
        try {
          await this.$axios.delete(`/v1/groups/delete/${groupId}/`);
          this.fetchGroups();
          alert("Group deleted successfully!");
        } catch (error) {
          console.error('Error deleting group:', error.response?.data);
          let message = "Sorry, we couldn't delete the group right now. Please try again in a few moments.";
          if (error.response?.data?.detail) {
            message = error.response.data.detail;
          }
          alert(message);
        }
      }
    }
  }
};
</script>