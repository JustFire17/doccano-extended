<template>
  <v-card>
    <!-- Botão para abrir o pop-up -->
    <v-btn class="text-capitalize mt-4" color="primary" @click="dialog = true">
      {{ $t("generic.create") }}
    </v-btn>

    <!-- Pop Up para Criar User -->
    <CreatePopUp
      :dialog.sync="dialog"
      :available-groups="availableGroups"
      @save-user="handleSaveUser"
    />

    <!-- Tabela de Users -->
    <v-data-table
      :headers="headers"
      :items="users"
      :options.sync="options"
      :server-items-length="total"
      :search="search"
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
      show-select
    >
      <!-- Barra de Pesquisa -->
      <template #top>
        <v-text-field
          v-model="search"
          prepend-inner-icon="mdi-magnify"
          :label="$t('generic.search')"
          single-line
          hide-details
          filled
          @input="handleSearch"
        />
      </template>

      <!-- Slot personalizado para a coluna "Actions" -->
      <template #[`item.actions`]="{ item }">
        <v-btn color="primary" text @click="openEditDialog(item)">
          {{ $t("generic.edit") }}
        </v-btn>
        <v-btn color="red" text @click="deleteUser(item.id)">
          {{ $t("generic.delete") }}
        </v-btn>
        <v-btn color="yellow" text @click="viewUser(item)">
            {{ $t("generic.viewUser") }}
          </v-btn>
      </template>
    </v-data-table>
    <!-- Pop Up para ver detalhes do utilizador -->
    <v-dialog v-model="viewDialog" max-width="900px">
      <v-card>
        <v-card-title class="headline primary white--text">
          <v-icon left color="white">mdi-account</v-icon>
          User Details
        </v-card-title>
        <v-card-text class="pt-4">
          <v-container>
            <!-- Username Section -->
            <v-row class="mb-4">
              <v-col cols="12">
                <v-card outlined>
                  <v-card-subtitle class="text-h6 primary--text">
                    <v-icon left color="primary">mdi-account-circle</v-icon>
                    Username
                  </v-card-subtitle>
                  <v-card-text>
                    <v-chip color="primary" text-color="white" large>
                      {{ selectedUser.username || 'N/A' }}
                    </v-chip>
                    <v-chip v-if="selectedUser.is_superuser" color="red" text-color="white" class="ml-2">
                      <v-icon left small>mdi-star</v-icon>
                      Super User
                    </v-chip>
                    <v-chip v-if="selectedUser.is_staff" color="orange" text-color="white" class="ml-2">
                      <v-icon left small>mdi-account-tie</v-icon>
                      Staff
                    </v-chip>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>

            <!-- Personal Info Section -->
            <v-row class="mb-4">
              <v-col cols="12">
                <v-card outlined>
                  <v-card-subtitle class="text-h6 primary--text">
                    <v-icon left color="primary">mdi-account-details</v-icon>
                    Personal Information
                  </v-card-subtitle>
                  <v-card-text>
                    <v-row>
                      <v-col cols="6">
                        <v-text-field 
                          :value="selectedUser.first_name || 'Not provided'" 
                          label="First Name" 
                          readonly 
                          outlined
                          prepend-icon="mdi-account"
                        />
                      </v-col>
                      <v-col cols="6">
                        <v-text-field 
                          :value="selectedUser.last_name || 'Not provided'" 
                          label="Last Name" 
                          readonly 
                          outlined
                          prepend-icon="mdi-account"
                        />
                      </v-col>
                      <v-col cols="12">
                        <v-text-field 
                          :value="selectedUser.email || 'Not provided'" 
                          label="Email" 
                          readonly 
                          outlined
                          prepend-icon="mdi-email"
                        />
                      </v-col>
                    </v-row>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>

            <!-- Groups Section -->
            <v-row class="mb-4">
              <v-col cols="12">
                <v-card outlined>
                  <v-card-subtitle class="text-h6 primary--text">
                    <v-icon left color="primary">mdi-account-group</v-icon>
                    Groups & Permissions
                  </v-card-subtitle>
                  <v-card-text>
                    <div v-if="selectedUserGroupsDisplay.length > 0">
                      <v-chip
                        v-for="group in selectedUserGroupsDisplay"
                        :key="group"
                        color="green"
                        text-color="white"
                        class="ma-1"
                      >
                        <v-icon left small>mdi-account-group</v-icon>
                        {{ group }}
                      </v-chip>
                    </div>
                    <div v-else class="grey--text">
                      <v-icon left color="grey">mdi-information</v-icon>
                      No groups assigned
                    </div>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>

            <!-- Important Dates Section -->
            <v-row>
              <v-col cols="12">
                <v-card outlined>
                  <v-card-subtitle class="text-h6 primary--text">
                    <v-icon left color="primary">mdi-calendar-clock</v-icon>
                    Important Dates
                  </v-card-subtitle>
                  <v-card-text>
                    <v-row>
                      <v-col cols="6">
                        <v-text-field 
                          label="Last Login" 
                          :value="formattedDateLogin" 
                          readonly 
                          outlined
                          prepend-icon="mdi-login"
                          :color="formattedDateLogin === 'Never' ? 'grey' : 'primary'"
                        />
                      </v-col>
                      <v-col cols="6">
                        <v-text-field 
                          label="Date Joined" 
                          :value="formattedDateJoined" 
                          readonly 
                          outlined
                          prepend-icon="mdi-calendar-plus"
                          color="primary"
                        />
                      </v-col>
                    </v-row>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn 
            color="primary" 
            outlined 
            block
            style="text-align: center !important;"
            @click="viewDialog = false"
          >
            Close
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

      <!-- Pop Up para Editar User -->
      <v-dialog v-model="editDialog" max-width="700px">
        <v-card>
          <v-card-title class="headline">Edit User</v-card-title>
          <v-card-text>
            <v-form ref="editForm">
              <!-- Grupo: Dados Pessoais -->
              <v-card outlined class="mb-4">
                <v-card-title class="subtitle-1 font-weight-bold">Personal Details</v-card-title>
                <v-card-text>
                  <v-text-field
                      v-model="editUser.username"
                      label="Username"
                      required
                      hint="150 characters or fewer. Letter, digits and @/./+/-/_ only."
                      persistent-hint
                  />
                  <div v-if="usernameError" class="text-caption red--text mt-1">
                    {{ usernameError }}
                  </div>
                  <v-text-field
                      v-model="editUser.first_name"
                      label="First Name"
                      hint="The user's given name."
                      persistent-hint
                  />
                  <div v-if="firstNameError" class="text-caption red--text mt-1">
                    {{ firstNameError }}
                  </div>
                  <v-text-field
                      v-model="editUser.last_name"
                      label="Last Name"
                      hint="The user's surname or family name."
                      persistent-hint
                  />
                  <div v-if="lastNameError" class="text-caption red--text mt-1">
                    {{ lastNameError }}
                  </div>
                  <v-text-field
                      v-model="editUser.email"
                      label="Email Address"
                      type="email"
                      hint="User's email address used for authentication and notifications."
                      persistent-hint
                  />
                  <div v-if="emailError" class="text-caption red--text mt-1">
                    {{ emailError }}
                  </div>
                </v-card-text>
              </v-card>

              <!-- Grupo: Permissions -->
              <v-card outlined class="mb-4">
                <v-card-title class="subtitle-1 font-weight-bold">Permissions</v-card-title>
                <v-card-text>
                  <v-autocomplete
                      v-model="editUser.groups"
                      :items="availableGroups"
                      item-text="name"
                      item-value="id"
                      label="Groups"
                      hint="The groups this user belongs to. A user will get all permissions granted to each of their groups."
                      multiple
                      chips
                      persistent-hint
                  />
                  <div v-if="groupsError" class="text-caption red--text mt-1">
                    {{ groupsError }}
                  </div>
                </v-card-text>
              </v-card>

              <!-- Grupo: Change Password -->
              <v-card outlined class="mb-4">
                <v-card-title class="subtitle-1 font-weight-bold">Change Password</v-card-title>
                <v-card-text>
                  <v-text-field
                      v-model="editUser.new_password"
                      label="New Password"
                      type="password"
                      hint="Your password can't be too similar to your other personal information. 
                      Your password must contain at least 8 characters. 
                      Your password can't be a commonly used password."
                      persistent-hint
                      :hint-color="'red'"
                  />
                  <div v-if="passwordError" class="text-caption red--text mt-1">
                    {{ passwordError }}
                  </div>
                  <v-text-field
                      v-model="editUser.confirm_new_password"
                      label="Confirm New Password"
                      type="password"
                      hint="Confirm the new password."
                      persistent-hint
                  />
                </v-card-text>
              </v-card>
            </v-form>
            
            <!-- Mensagem de erro geral -->
            <div v-if="generalError" class="text-caption red--text mt-2">
              <v-alert type="error" dense outlined>
                {{ generalError }}
              </v-alert>
            </div>
          </v-card-text>
          <v-card-actions>
            <v-spacer />
            <v-btn color="red" text @click="editDialog = false">Cancel</v-btn>
            <v-btn color="primary" @click="saveUserChanges">Save</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
  </v-card>
</template>

<script>
import { debounce } from "lodash";
import CreatePopUp from "@/components/user/CreatePopUp.vue";

export default {
  components: {
    CreatePopUp
  },
  layout: "projects",
  middleware: ["check-auth", "auth"],
  data() {
    return {
      viewDialog: false,
      selectedUser: {
        id: null,
        username: '',
        first_name: '',
        last_name: '',
        email: '',
        groups: [],
        date_joined: null,
        last_log: null,
        is_staff: false,
        is_superuser: false
      },
      editDialog: false,
      editUser: {
        id: null,
        username: "",
        first_name: "",
        last_name: "",
        email: "",
        groups: [],
        new_password: "",
        confirm_new_password: ""
      },
      passwordError: "",
      usernameError: "",
      emailError: "",
      firstNameError: "",
      lastNameError: "",
      groupsError: "",
      generalError: "",
      dialog: false,
      search: "",
      isLoading: false,
      users: [],
      total: 0,
      options: {
        page: 1,
        itemsPerPage: 10,
        sortBy: ["username"],
        sortDesc: [false]
      },
      availableGroups: [],
      headers: [
        { text: "Username", value: "username" },
        { text: "First Name", value: "first_name" },
        { text: "Last Name", value: "last_name" },
        { text: "Email", value: "email" },
        { text: "Actions", value: "actions", sortable: false }
      ]
    };
  },
  computed: {
    formattedDateJoined() {
      if (!this.selectedUser?.date_joined) return 'Never';
      try {
        const date = new Date(this.selectedUser.date_joined);
        if (isNaN(date.getTime())) return 'Invalid date';
        
        const day = String(date.getDate()).padStart(2, '0');
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const year = date.getFullYear();
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        return `${day}/${month}/${year} às ${hours}:${minutes}`;
      } catch (error) {
        console.error('Error formatting date joined:', error);
        return 'Invalid date';
      }
    },
    formattedDateLogin() {
      if (!this.selectedUser?.last_log) return 'Never';
      try {
        const date = new Date(this.selectedUser.last_log);
        if (isNaN(date.getTime())) return 'Invalid date';
        
        const day = String(date.getDate()).padStart(2, '0');
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const year = date.getFullYear();
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        return `${day}/${month}/${year} às ${hours}:${minutes}`;
      } catch (error) {
        console.error('Error formatting last login:', error);
        return 'Invalid date';
      }
    },
    
    selectedUserGroupsDisplay() {
      if (!this.selectedUser?.groups || !Array.isArray(this.selectedUser.groups)) {
        return [];
      }
      
      // If groups are IDs, map them to group names
      if (this.selectedUser.groups.length > 0 && typeof this.selectedUser.groups[0] === 'number') {
        return this.selectedUser.groups.map(groupId => {
          const group = this.availableGroups.find(g => g.id === groupId);
          return group ? group.name : `Group ${groupId}`;
        });
      }
      
      // If groups are already objects or strings, return as is
      return this.selectedUser.groups;
    }
  },
  mounted() {
    this.isAdminUserCheck();
    this.fetchUsers();
    this.fetchGroups();
  },
  methods: {
    toggleOptionalFields() {
      this.showOptionalFields = !this.showOptionalFields;
    },
    async viewUser(user) {
      try {
        this.viewDialog = true;
        
        // Initialize with basic user data first
        this.selectedUser = {
          id: user.id || null,
          username: user.username || '',
          first_name: user.first_name || '',
          last_name: user.last_name || '',
          email: user.email || '',
          groups: user.groups || [],
          date_joined: user.date_joined || null,
          last_log: user.last_log || null,
          is_staff: user.is_staff || false,
          is_superuser: user.is_superuser || false
        };

        // Fetch detailed user information using services/repositories
        const userDetails = await this.$services.user.getById(user.id);
        
        // Update with detailed information
        this.selectedUser = {
          ...this.selectedUser,
          ...userDetails
        };

      } catch (error) {
        console.error("Error fetching user details:", error);
        this.viewDialog = false;
        
        if (error.response?.status === 500) {
          alert("Database unavailable. Please try again later.");
        } else if (error.response?.status === 404) {
          alert("User not found.");
        } else {
          alert("Error fetching user details: " + (error.message || 'Unknown error'));
        }
      }
    },
    openEditDialog(user) {
      // Limpar todos os erros anteriores
      this.passwordError = "";
      this.usernameError = "";
      this.emailError = "";
      this.firstNameError = "";
      this.lastNameError = "";
      this.groupsError = "";
      this.generalError = "";
      
      this.editUser = {
        id: user.id || null,
        username: user.username || "",
        first_name: user.first_name || "",
        last_name: user.last_name || "",
        email: user.email || "",
        groups: user.groups || [],
        new_password: "",
        confirm_new_password: "",
      };
      this.editDialog = true;
    },
    async saveUserChanges() {
      try {
        // Limpar todos os erros anteriores
        this.passwordError = "";
        this.usernameError = "";
        this.emailError = "";
        this.firstNameError = "";
        this.lastNameError = "";
        this.groupsError = "";
        this.generalError = "";
        
        const userData = {
          id: this.editUser.id,
          username: this.editUser.username,
          first_name: this.editUser.first_name,
          last_name: this.editUser.last_name,
          email: this.editUser.email,
          groups: this.editUser.groups
        };

        await this.$services.user.updateWithPassword(
          userData,
          this.editUser.new_password,
          this.editUser.confirm_new_password
        );

        this.fetchUsers();
        this.editDialog = false;
        alert("User updated successfully!");
      } catch (error) {
        console.error("Error updating user:", error);
        console.log("Error response data:", error.response?.data);
        console.log("Error message:", error.message);
        
        // Processar erros específicos por campo
        if (error.response?.data) {
          const errorData = error.response.data;
          
          // Erros de password
          if (errorData.new_password) {
            this.passwordError = Array.isArray(errorData.new_password) 
              ? errorData.new_password.join(" ") 
              : errorData.new_password;
          } else if (errorData.password) {
            this.passwordError = Array.isArray(errorData.password) 
              ? errorData.password.join(" ") 
              : errorData.password;
          }
          
          // Erros de username
          if (errorData.username) {
            this.usernameError = Array.isArray(errorData.username) 
              ? errorData.username.join(" ") 
              : errorData.username;
          }
          
          // Erros de email
          if (errorData.email) {
            this.emailError = Array.isArray(errorData.email) 
              ? errorData.email.join(" ") 
              : errorData.email;
          }
          
          // Erros de first_name
          if (errorData.first_name) {
            this.firstNameError = Array.isArray(errorData.first_name) 
              ? errorData.first_name.join(" ") 
              : errorData.first_name;
          }
          
          // Erros de last_name
          if (errorData.last_name) {
            this.lastNameError = Array.isArray(errorData.last_name) 
              ? errorData.last_name.join(" ") 
              : errorData.last_name;
          }
          
          // Erros de groups
          if (errorData.groups) {
            this.groupsError = Array.isArray(errorData.groups) 
              ? errorData.groups.join(" ") 
              : errorData.groups;
          }
          
          // Erros gerais (non-field errors)
          if (errorData.non_field_errors) {
            this.generalError = Array.isArray(errorData.non_field_errors) 
              ? errorData.non_field_errors.join(" ") 
              : errorData.non_field_errors;
          }
          
          // Se não há erros específicos, mostrar erro geral
          if (!this.passwordError && !this.usernameError && !this.emailError && 
              !this.firstNameError && !this.lastNameError && !this.groupsError && 
              !this.generalError) {
            this.generalError = "An error occurred while updating the user. Please check your data and try again.";
          }
          
        } else if (error.message) {
          // Tratamento de erro da mensagem (mantendo compatibilidade com password)
          const errorMessage = error.message;
          if (errorMessage.includes('password') || errorMessage.includes('Password')) {
            const match = errorMessage.match(/\[(.*?)\]/);
            if (match) {
              this.passwordError = match[1].replace(/'/g, '');
            } else {
              this.passwordError = errorMessage;
            }
          } else {
            this.generalError = errorMessage;
          }
        } else {
          this.generalError = "An unexpected error occurred. Please try again.";
        }
      }
    },
    async fetchUsers() {
      try {
        this.isLoading = true;
        const response = await this.$services.user.list();
        this.users = response;
        this.total = response.length;
      } catch (error) {
        console.error("Error getting users:", error);
        this.$store.dispatch('snackbar/showError', 'Error loading users');
      } finally {
        this.isLoading = false;
      }
    },
    async fetchGroups() {
      try {
        const response = await this.$axios.get("/v1/groups");
        this.availableGroups = response.data;
      } catch (error) {
        console.error("Erro ao obter grupos:", error);
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
    handleSearch: debounce(function () {
      this.fetchUsers(this.search);
    }, 300),

    async handleSaveUser(newUser) {
      try {
        await this.$axios.post("/v1/users/create", newUser);
        this.fetchUsers();
        alert("User created successfully!");
      } catch (error) {
          console.error("Error creating user:", error);
          if (error.response?.status === 500) {
            alert("Database is currently unavailable. Please try again later.");
          } else if (error.response?.data) {
            const errorMessages = Object.values(error.response.data)
              .flat()
              .join(" ");
            alert(errorMessages);
          } else {
            alert("Error creating user: " + error.message);
          }
        }
    },

    async deleteUser(userId) {
      if (confirm("Are you sure you want to delete this user?")) {
        try {
          const response = await this.$axios.delete(`/v1/users/delete/${userId}`);
          if (response.status === 200) {
            // User was deactivated instead of deleted
            alert("This user is associated with projects and cannot be deleted. They have been deactivated instead.");
          } else {
            alert("User deleted successfully!");
          }
          this.fetchUsers();
        } catch (error) {
          console.error("Error deleting user:", error.response?.data);
          // Verificar se o erro está relacionado à conexão com o banco de dados
          if (error.response.status === 500) {
            alert("Error: Unable to connect to the database. Please try again later.");
          } else {
            alert("Error deleting user: " + (error.response.data?.detail || error.message));
          }
        }
      }
    }
  },
};
</script>