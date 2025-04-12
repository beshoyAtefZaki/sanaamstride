<!-- script setup block using Composition API -->
<script setup>
// Import Vue's reactivity and lifecycle functions
import { ref, onMounted, computed } from 'vue'

// Create a reactive variable to store the projects
const projects = ref([])
const searchQuery = ref('')

// When the component is mounted to the DOM, fetch the projects
onMounted(async () => {
  try { 
    var url = 'http://192.168.3.23:8002/api/method/sanaamstride.api.project.get_all'
    var token = 'f4d8bec94019549:4584c9b5c873763'
    // Call the API to get project data
    const response = await fetch(url , {method: 'GET' , headers: {'Authorization': 'token ' + token}}) 

    // Parse the response as JSON and update the reactive variable
    const data = await response.json()
    projects.value = data.message || []
  } catch (error) {
    // Log any errors to the console
    console.error('Error:', error)
  }
})

// Computed property to filter projects based on search query
const filteredProjects = computed(() => {
  if (!searchQuery.value) return projects.value
  const query = searchQuery.value.toLowerCase()
  return projects.value.filter(project => 
    project.project_name.toLowerCase().includes(query)
  )
})
</script>

<!-- template section for the component's HTML -->
<template>
  <main>
    <h1>Projects List</h1>
    
    <!-- Search input for filtering projects -->
    <div class="search-container">
      <input 
        type="text" 
        v-model="searchQuery" 
        placeholder="Search by project name..."
        class="search-input"
      />
    </div>

    <!-- Display the hierarchical project structure -->
    <div class="projects-container">
      <div v-for="project in filteredProjects" :key="project.name" class="project-card">
        <!-- Project ID -->
        <div class="project-id-section">
          <span class="label">Project ID:</span>
          <span class="value">{{ project.name }}</span>
        </div>

        <!-- Project Name -->
        <div class="project-name-section">
          <span class="label">Project Name:</span>
          <span class="value">{{ project.project_name }}</span>
        </div>

        <!-- Child Projects -->
        <div v-if="project.child_projects && project.child_projects.length" class="child-projects">
          <div class="section-label">Child Projects:</div>
          <div v-for="child in project.child_projects" :key="child.name" class="child-project">
            <!-- Child Project ID -->
            <div class="child-id-section">
              <span class="label">Child Project ID:</span>
              <span class="value">{{ child.name }}</span>
            </div>

            <!-- Child Project Name -->
            <div class="child-name-section">
              <span class="label">Child Project Name:</span>
              <span class="value">{{ child.project_name }}</span>
            </div>

            <!-- Sprints -->
            <div v-if="child.sprints && child.sprints.length" class="sprints">
              <div class="section-label">Sprints:</div>
              <div v-for="sprint in child.sprints" :key="sprint.name" class="sprint-item">
                <span class="label">Sprint ID:</span>
                <span class="value">{{ sprint.name }}</span>
                <span class="label">Sprint Name:</span>
                <span class="value">{{ sprint.sprint_name }}</span>
              </div>
            </div>

            <!-- Tasks -->
            <div v-if="child.tasks && child.tasks.length" class="tasks">
              <div class="section-label">Tasks:</div>
              <div v-for="task in child.tasks" :key="task.name" class="task-item">
                <span class="label">Task ID:</span>
                <span class="value">{{ task.name }}</span>
                <span class="label">Task Name:</span>
                <span class="value">{{ task.task_name }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>

<!-- scoped style so it only applies to this component -->
<style scoped>
main {
  padding: 20px;
  font-family: Arial, sans-serif;
}

h1 {
  color: #333;
  margin-bottom: 10px;
}

.search-container {
  margin-bottom: 20px;
}

.search-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

.projects-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.project-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  background-color: #f9f9f9;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.project-id-section, .project-name-section {
  margin-bottom: 15px;
  padding: 10px;
  background-color: #fff;
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.label {
  font-weight: 600;
  color: #333;
  margin-right: 10px;
}

.value {
  color: #666;
}

.section-label {
  font-weight: 600;
  color: #444;
  margin: 15px 0 10px 0;
  padding-left: 10px;
  border-left: 3px solid #2196f3;
}

.child-projects {
  margin-left: 20px;
  padding-left: 20px;
  border-left: 2px solid #ddd;
}

.child-project {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #fff;
  border-radius: 6px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.child-id-section, .child-name-section {
  margin-bottom: 10px;
  padding: 8px;
  background-color: #f5f5f5;
  border-radius: 4px;
}

.sprints, .tasks {
  margin-left: 20px;
  margin-top: 15px;
}

.sprint-item, .task-item {
  margin: 8px 0;
  padding: 10px;
  background-color: #f5f5f5;
  border-radius: 4px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.sprints .section-label {
  border-left-color: #8bc34a;
}

.tasks .section-label {
  border-left-color: #2196f3;
}
</style>

