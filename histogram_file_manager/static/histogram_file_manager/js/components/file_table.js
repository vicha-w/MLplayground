app.component('file-table', {
    template:
        /*html*/
        `
<div>
 <table class="table">
   <tr>
     <th scope="col"
	   v-for="header in headers"
	   :key="header">
	   {{ header }}
	 </th>
     <th>Actions</th>
   </tr>
  <tr v-for="file_information of files_information">
    <td v-for="value of file_information">
	  {{ value }}
	</td>
	<td>
	  <div class="col">
		<div class="row">
		  <button 
			v-on:click="file_actions_clicked(file_information)"
			:class="{disabled: file_information.percentage_processed === 100.0 }"
			>
			Actions
		  </button>
		</div>
	  </div>
	</td>
  </tr>
</table>   
</div>
`,
    methods: {
        // Callback for Parsing button, takes the id of the file as parameter
        file_actions_clicked(file_information) {
            this.$emit('file-actions-clicked', file_information);
            // console.debug(`Sending parse command for file ${file_id}`);
        },
    },
    props: {
        // headers: {
        //     type: Array,
        //     required: true,
        // },
        // Array of objects
        files_information: {
            type: Array,
            required: true,
        },
    },
    computed: {
        headers() {
            if (this.files_information.length > 0) {
                return Object.keys(this.files_information[0]);
            } else {
                return [];
            }
        },
    },
});
