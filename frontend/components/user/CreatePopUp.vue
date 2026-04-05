<template>
  <v-dialog :value="dialog" max-width="500px" @input="updateDialog">
    <v-card>
      <v-card-title class="headline">Add User</v-card-title>
      <v-card-text>
        <v-form ref="form" v-model="valid">
          <v-text-field 
            v-model="username" 
            label="Username" 
            :rules="[rules.required]"
            hint="150 characters or fewer. Letter, digits and @/./+/-/_ only."
            persistent-hint
          />
          <v-text-field 
            v-model="email" 
            label="Email Address" 
            persistent-hint
            :rules="[rules.required, rules.validEmail]"
          />
          <v-text-field 
            v-model="password" 
            label="Password" 
            type="password" 
            :rules="[rules.required]"
            hint="Your password can't be too similar to your other personal information. 
            Your password must contain at least 8 characters. 
            Your password can't be a commonly used password."
            persistent-hint
          />
          <v-text-field 
            v-model="passwordConfirm" 
            label="Password confirmation" 
            type="password" 
            :rules="[rules.required]"
          />

          <v-btn text color="primary" @click="toggleOptionalFields">
            {{ showOptionalFields ? 'Hide Optional Fields' : 'Show Optional Fields' }}
          </v-btn>

          <v-expand-transition>
            <div v-if="showOptionalFields">
              <v-text-field 
                v-model="first_name" 
                label="First Name" 
                hint="The user's given name."
                persistent-hint
              />
              <v-text-field 
                v-model="last_name" 
                label="Last Name" 
                hint="The user's surname or family name."
                persistent-hint
              />
              <v-autocomplete
                v-model="groups"
                :items="availableGroups"
                item-text="name"
                item-value="id"
                label="Groups"
                hint="The groups this user belongs to. A user will get all permissions granted to each of their groups."
                multiple
                chips
                persistent-hint
              />
            </div>
          </v-expand-transition>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn color="red" text @click="closeDialog">Cancel</v-btn>
        <v-btn :disabled="!valid" color="primary" @click="saveUser">Save</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  props: {
    dialog: {
      type: Boolean,
      required: true
    },
    availableGroups: {
      type: Array,
      required: true
    }
  },
  data() {
    return {
      valid: false,
      showOptionalFields: false,
      username: "",
      email: "",
      first_name: "",
      last_name: "",
      password: "",
      passwordConfirm: "",
      groups: [],
      rules: {
        required: (v) => !!v || "This field is required",
        validEmail: (v) => {
          const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
          return emailRegex.test(v) || "Please enter a valid email address";
        }
      }
    };
  },
  methods: {
    toggleOptionalFields() {
      this.showOptionalFields = !this.showOptionalFields;
    },
    updateDialog(value) {
      this.$emit("update:dialog", value);
    },
    closeDialog() {
      this.updateDialog(false);
    },
    resetForm() {
      if (this.$refs.form) {
        this.$refs.form.reset();
      }
      this.showOptionalFields = false;
    },
    async saveUser() {
      if (this.password !== this.passwordConfirm) {
        alert("The passwords are different!");
        return;
      }
        const newUser = {
          username: this.username,
          password1: this.password,
          password2: this.passwordConfirm,
          email: this.email,
          first_name: this.first_name || "",
          last_name: this.last_name || "",
          groups: this.groups || []
        };
        await this.$emit("save-user", newUser);
        this.resetForm();
        this.closeDialog();
    }
  }
};
</script>