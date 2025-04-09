<!-- script setup block using Composition API -->
<script setup>
// Import Vue's reactivity and lifecycle functions
import { ref, onMounted } from 'vue'

// Create a reactive variable to store the users
const users = ref([])

// When the component is mounted to the DOM, fetch the users
onMounted(async () => {
  try {
    // Call the API to get user data
    const response = await fetch('https://jsonplaceholder.typicode.com/users')

    // Parse the response as JSON and update the reactive variable
    users.value = await response.json()
  } catch (error) {
    // Log any errors to the console
    console.error('Error:', error)
  }
})
</script>

<!-- template section for the component's HTML -->
<template>
  <main>
    <h1>Users List</h1>

    <!-- Loop through the users array and display each user's name -->
    <ul>
      <li v-for="user in users" :key="user.id">
        {{ user.name }}
      </li>
    </ul>
  </main>
</template>

<!-- scoped style so it only applies to this component -->
<style scoped>
/* You can add custom styles here */
main {
  padding: 20px;
  font-family: Arial, sans-serif;
}

h1 {
  color: #333;
  margin-bottom: 10px;
}

ul {
  list-style: none;
  padding-left: 0;
}

li {
  padding: 6px 0;
  border-bottom: 1px solid #eee;
}
</style>
