(function(){
  const container = document.getElementById('api-buttons');
  const respEl = document.getElementById('api-response');
  const responseInfo = document.getElementById('response-info');
  const successCountEl = document.getElementById('success-count');
  const errorCountEl = document.getElementById('error-count');
  const totalRequestsEl = document.getElementById('total-requests');
  
  if(!container) return;
  
  let successCount = 0, errorCount = 0, totalRequests = 0;
  
  function updateStats() {
    if(successCountEl) successCountEl.textContent = successCount;
    if(errorCountEl) errorCountEl.textContent = errorCount;
    if(totalRequestsEl) totalRequestsEl.textContent = totalRequests;
  }
  
  // Clear response button
  const clearBtn = document.getElementById('clear-response');
  if(clearBtn) {
    clearBtn.addEventListener('click', () => {
      respEl.textContent = 'Response cleared...';
      respEl.style.color = '#666';
      if(responseInfo) responseInfo.textContent = '';
    });
  }

  const endpoints = [
    {label:'Register User ✅', method:'POST', url:'/api/users/register/', body:{email:'test'+Date.now()+'@example.com',password:'Aa!23456'}},
    {label:'Login (sample) ✅', method:'POST', url:'/api/users/login/', body:{email:'admin@example.com',password:'AdminPass123!'}},
    {label:'Team Members ✅', method:'GET', url:'/api/team/members/'},
    {label:'User Profile ✅', method:'GET', url:'/api/users/profile/'},
    {label:'Update Profile ✅', method:'PATCH', url:'/api/users/profile/', body:{first_name:'New', last_name:'Name'}},
    {label:'Logout (API) ✅', method:'POST', url:'/api/users/logout/'},
    {label:'Token Obtain (raw) ✅', method:'POST', url:'/api/users/token/', body:{email:'admin@example.com',password:'AdminPass123!'}},
    {label:'Token Refresh ✅', method:'POST', url:'/api/users/token/refresh/', body:()=>({refresh:localStorage.getItem('refreshToken')})},
    {label:'Token Verify ✅', method:'POST', url:'/api/users/token/verify/', body:()=>({token:localStorage.getItem('accessToken')})},
    {label:'Projects List ✅', method:'GET', url:'/projects/api/projects/'},
    {label:'Create Project ✅', method:'POST', url:'/projects/api/projects/', body:{name:'Auto '+Date.now(), description:'Created via explorer'}},
    {label:'Tasks List ✅', method:'GET', url:'/tasks/api/tasks/'},
    {label:'Chat Rooms ✅', method:'GET', url:'/chat/api/rooms/'},
    {label:'Chat Messages ✅', method:'GET', url:'/chat/api/messages/'},
    {label:'Notifications List ✅', method:'GET', url:'/notifications/'},
    {label:'Notifications Count ✅', method:'GET', url:'/notifications/count/'},
    {label:'Mark All Notifications Read ✅', method:'POST', url:'/notifications/mark-all-read/'},
    {label:'Dashboard Stats ✅', method:'GET', url:'/dashboard/stats/'},
    {label:'Analytics Reports ✅', method:'GET', url:'/analytics/api/reports/'},
    {label:'AI Productivity ✅', method:'GET', url:'/ai/productivity/'},
    {label:'AI Suggestions ✅', method:'GET', url:'/ai/suggestions/'},
    {label:'Payments Stripe ✅', method:'GET', url:'/payments/stripe/'},
    {label:'Core Test ✅', method:'GET', url:'/core/test/'},
    {label:'Global Search ✅', method:'GET', url:'/api/search/?q=test'},
    {label:'Recent Activity ✅', method:'GET', url:'/api/activity/recent/'},
    // Additional useful endpoints
    {label:'Create Task (Auto Project)', method:'POST', url:'/tasks/api/tasks/', body:async ()=>{
      // First try to get a project, or create one
      try {
        const projects = await fetch('/projects/api/projects/', {
          headers: {'Authorization': 'Bearer ' + (localStorage.getItem('accessToken')||'')}
        }).then(r=>r.json());
        const projectId = projects.results && projects.results.length > 0 ? projects.results[0].id : null;
        if(projectId) {
          return {title:'Test Task '+Date.now(), description:'Created from explorer', project: projectId};
        } else {
          // Create a project first
          const newProject = await fetch('/projects/api/projects/', {
            method: 'POST',
            headers: {'Content-Type':'application/json', 'Authorization': 'Bearer ' + (localStorage.getItem('accessToken')||'')},
            body: JSON.stringify({name: 'Auto Project '+Date.now(), description: 'Created for task'})
          }).then(r=>r.json());
          return {title:'Test Task '+Date.now(), description:'Created from explorer', project: newProject.id};
        }
      } catch {
        return {title:'Test Task '+Date.now(), description:'Created from explorer (no project)', project: null};
      }
    }},
    {label:'Create Task (Simple)', method:'POST', url:'/tasks/api/tasks/', body:{title:'Simple Task '+Date.now(), description:'No project assigned'}},
    {label:'Create Comment', method:'POST', url:'/tasks/api/comments/', body:{content:'Test comment', task_id:1}},
    {label:'AI Chat Test', method:'POST', url:'/ai/chat/', body:{message:'Hello AI'}},
    {label:'Generate Task AI', method:'POST', url:'/ai/generate-task/', body:{description:'Create a sample task'}},
  ];

  function makeButton(ep){
    const btn = document.createElement('button');
    btn.className = 'btn btn-sm';
    btn.style.padding = '8px';
    btn.textContent = ep.label;
    btn.addEventListener('click', async () => {
      respEl.textContent = 'Loading...';
      respEl.style.color = '#ff0';
      if(responseInfo) responseInfo.textContent = `Testing ${ep.method} ${ep.url}...`;
      
      totalRequests++;
      updateStats();
      
      let bodyData = null;
      if(ep.body){
        bodyData = typeof ep.body === 'function' ? ep.body() : ep.body;
      }
      try {
        const options = {
          method: ep.method,
          headers:{'Content-Type':'application/json'}
        };
        
        // Add auth token if available
        const token = localStorage.getItem('accessToken');
        if(token) {
          options.headers['Authorization'] = 'Bearer ' + token;
        }
        
        if(bodyData) options.body = JSON.stringify(bodyData);
        
        const response = await fetch(ep.url, options);
        const status = response.status;
        
        let result;
        try {
          result = await response.json();
        } catch {
          result = {error: 'Non-JSON response', status: status, text: await response.text()};
        }
        
        const output = {
          status: status,
          ok: response.ok,
          url: ep.url,
          method: ep.method,
          data: result,
          timestamp: new Date().toISOString()
        };
        
        // If validation error, show helpful message
        if (status === 400 && result && typeof result === 'object') {
          output.validation_help = "This is a validation error. Check required fields and data formats.";
        }
        
        respEl.textContent = JSON.stringify(output, null, 2);
        respEl.style.color = response.ok ? '#0f0' : '#f44';
        
        if(response.ok) successCount++; else errorCount++;
        updateStats();
        
        if(responseInfo) responseInfo.textContent = `Status: ${status} | Time: ${new Date().toLocaleTimeString()}`;
        
      } catch(err){
        respEl.textContent = 'NETWORK ERROR:\n' + (err.message || String(err));
        respEl.style.color = '#f44';
        errorCount++;
        updateStats();
        if(responseInfo) responseInfo.textContent = 'Network Error | ' + new Date().toLocaleTimeString();
      }
    });
    return btn;
  }

  endpoints.forEach(ep => container.appendChild(makeButton(ep)));
})();