class SendaApp {
  constructor() {
    this.apiBase = '/api/v1';
    this.token = sessionStorage.getItem('senda_token');
    this.user = JSON.parse(sessionStorage.getItem('senda_user'));
    this.currentStatusFilter = 'publicado'; // default feed filter
    this.searchQuery = '';
    this.activeComments = {}; // maps writing_id -> list of comments

    // Bind methods
    this.init();
  }

  init() {
    this.updateAuthUI();
    this.fetchWritings();
  }

  // Auth helper methods
  updateAuthUI() {
    const authContainer = document.getElementById('auth-container');
    const adminPanel = document.getElementById('admin-panel');
    const filterBorradores = document.getElementById('filter-borradores');

    if (this.token && this.user) {
      // User is logged in
      const roleText = this.user.role === 'admin' ? 'Escritor' : 'Lector';
      const roleColor = this.user.role === 'admin' ? 'bg-purple-900/60 text-purple-300' : 'bg-blue-900/60 text-blue-300';
      
      authContainer.innerHTML = `
        <div class="flex items-center gap-3">
          <div class="flex flex-col text-right hidden md:block">
            <span class="text-sm font-semibold text-gray-200">${this.user.name}</span>
            <span class="text-[10px] self-end px-2 py-0.5 rounded-full ${roleColor}">${roleText}</span>
          </div>
          <button onclick="app.handleLogout()" class="px-3 py-1.5 rounded-xl border border-gray-800 hover:border-red-500 hover:text-red-500 text-gray-400 font-medium text-xs transition duration-200">
            <i class="fa-solid fa-right-from-bracket mr-1"></i>
            Salir
          </button>
        </div>
      `;

      if (this.user.role === 'admin') {
        adminPanel.classList.remove('hidden');
        filterBorradores.classList.remove('hidden');
      } else {
        adminPanel.classList.add('hidden');
        filterBorradores.classList.add('hidden');
      }
    } else {
      // User is not logged in
      authContainer.innerHTML = `
        <button onclick="app.openLoginModal()" class="flex items-center gap-2 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-medium text-sm transition duration-200 shadow-md shadow-blue-600/10">
          <i class="fa-solid fa-right-to-bracket"></i>
          Ingresar
        </button>
      `;
      adminPanel.classList.add('hidden');
      filterBorradores.classList.add('hidden');
    }
  }

  openLoginModal() {
    document.getElementById('login-modal').classList.remove('hidden');
  }

  closeLoginModal() {
    document.getElementById('login-modal').classList.add('hidden');
  }

  async handleLogin(event) {
    event.preventDefault();
    const email = document.getElementById('login-email').value;
    const role = document.querySelector('input[name="login-role"]:checked').value;

    try {
      const response = await fetch(`${this.apiBase}/auth/developer-login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, role })
      });

      if (!response.ok) {
        throw new Error('Error al iniciar sesión');
      }

      const data = await response.json();
      this.token = data.access_token;
      this.user = data.user;

      sessionStorage.setItem('senda_token', this.token);
      sessionStorage.setItem('senda_user', JSON.stringify(this.user));

      this.closeLoginModal();
      this.updateAuthUI();
      
      // Reset filter and refresh feed
      this.changeFeedFilter(this.user.role === 'admin' ? '' : 'publicado');
    } catch (err) {
      alert(err.message);
    }
  }

  handleLogout() {
    sessionStorage.removeItem('senda_token');
    sessionStorage.removeItem('senda_user');
    this.token = null;
    this.user = null;
    this.updateAuthUI();
    this.changeFeedFilter('publicado');
  }

  // Writings management
  async fetchWritings() {
    const feedContainer = document.getElementById('feed-container');
    const feedTitle = document.getElementById('feed-title');
    
    let url = `${this.apiBase}/writings/`;
    
    if (this.searchQuery) {
      url = `${this.apiBase}/writings/search?q=${encodeURIComponent(this.searchQuery)}`;
      feedTitle.textContent = `Resultados de búsqueda: "${this.searchQuery}"`;
    } else {
      const params = new URLSearchParams();
      if (this.currentStatusFilter) {
        params.append('status', this.currentStatusFilter);
      }
      url += '?' + params.toString();
      
      const filterLabels = {
        '': 'Todos los Escritos',
        'publicado': 'Escritos Publicados',
        'borrador': 'Borradores de Autor'
      };
      feedTitle.textContent = filterLabels[this.currentStatusFilter] || 'Escritos';
    }

    try {
      const headers = {};
      if (this.token) {
        headers['Authorization'] = `Bearer ${this.token}`;
      }

      const response = await fetch(url, { headers });
      if (!response.ok) {
        throw new Error('Error al cargar escritos');
      }

      const writings = await response.json();
      this.renderFeed(writings);
    } catch (err) {
      feedContainer.innerHTML = `
        <div class="glass-card p-8 rounded-2xl border border-red-500/20 text-center text-red-400">
          <i class="fa-solid fa-triangle-exclamation text-3xl mb-2"></i>
          <p>${err.message}</p>
        </div>
      `;
    }
  }

  renderFeed(writings) {
    const feedContainer = document.getElementById('feed-container');
    
    if (writings.length === 0) {
      feedContainer.innerHTML = `
        <div class="glass-card p-12 rounded-2xl text-center text-gray-500 border border-gray-800/40">
          <i class="fa-solid fa-folder-open text-4xl mb-3 text-gray-600"></i>
          <p class="text-lg font-medium">No se encontraron escritos</p>
          <p class="text-xs text-gray-600 mt-1">Escribe tu primer poema o cambia el filtro de búsqueda</p>
        </div>
      `;
      return;
    }

    feedContainer.innerHTML = writings.map(w => {
      const dateStr = new Date(w.created_at).toLocaleDateString('es-ES', {
        year: 'numeric', month: 'long', day: 'numeric'
      });
      
      const statusPill = w.status === 'borrador' 
        ? `<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-900/60 text-amber-300 border border-amber-800/30 uppercase tracking-wide">Borrador</span>`
        : '';

      const tagsHTML = w.tags && w.tags.length > 0
        ? w.tags.map(t => `<span class="px-2.5 py-0.5 rounded-full text-xs bg-gray-900 border border-gray-800 text-gray-400 hover:text-blue-400 cursor-pointer" onclick="app.searchTag('${t}')">#${t}</span>`).join(' ')
        : '';

      const adminButtons = this.user && this.user.role === 'admin'
        ? `
          <div class="flex items-center gap-2">
            <button onclick="app.editWriting(${w.id})" class="p-2 rounded-lg bg-gray-900 hover:bg-gray-800 text-blue-400 hover:text-blue-300 transition duration-200 border border-gray-800 text-xs flex items-center gap-1">
              <i class="fa-solid fa-pen"></i> Editar
            </button>
            <button onclick="app.deleteWriting(${w.id})" class="p-2 rounded-lg bg-gray-900 hover:bg-gray-800 text-red-400 hover:text-red-300 transition duration-200 border border-gray-800 text-xs flex items-center gap-1">
              <i class="fa-solid fa-trash"></i> Eliminar
            </button>
          </div>
        `
        : '';

      return `
        <article class="glass-card rounded-2xl border border-gray-800/50 hover:border-gray-700/60 transition duration-300 overflow-hidden flex flex-col">
          <!-- Content Body -->
          <div class="p-6 sm:p-8 flex flex-col gap-4 border-b border-gray-800/40">
            <div class="flex items-start justify-between gap-4">
              <div class="flex flex-col gap-1.5">
                <div class="flex items-center gap-2">
                  <h3 class="text-xl sm:text-2xl font-bold tracking-tight text-gray-100 hover:text-blue-400 transition cursor-pointer" onclick="app.viewSingleWriting(${w.id})">
                    ${w.title}
                  </h3>
                  ${statusPill}
                </div>
                <div class="flex items-center gap-2 text-xs text-gray-500">
                  <span>Por Escritor Principal</span>
                  <span>•</span>
                  <span>${dateStr}</span>
                </div>
              </div>
              ${adminButtons}
            </div>

            <div class="markdown-body text-gray-300 text-sm sm:text-base prose prose-invert max-w-none">
              ${marked.parse(w.content)}
            </div>

            <!-- Tags -->
            <div class="flex flex-wrap gap-2 mt-2">
              ${tagsHTML}
            </div>
          </div>

          <!-- Comments Feed Section -->
          <div class="bg-gray-950/20 p-6 sm:p-8 flex flex-col gap-5">
            <h4 class="text-sm font-bold text-gray-400 uppercase tracking-wider flex items-center gap-2 mb-1">
              <i class="fa-regular fa-comments text-blue-500"></i>
              Comentarios y Valoraciones
            </h4>

            <div id="comments-list-${w.id}" class="flex flex-col gap-4">
              <!-- Dynamically loaded comments -->
              <button onclick="app.loadComments(${w.id})" class="text-xs text-blue-400 hover:text-blue-300 transition text-left self-start flex items-center gap-1.5">
                <i class="fa-solid fa-arrow-down-short-wide"></i> Mostrar comentarios...
              </button>
            </div>

            <!-- Add Comment Form -->
            ${this.renderCommentForm(w.id)}
          </div>
        </article>
      `;
    }).join('');
  }

  // Comments logic
  renderCommentForm(writingId) {
    if (!this.token) {
      return `
        <div class="text-center p-4 border border-dashed border-gray-800 rounded-xl bg-gray-900/10 text-xs text-gray-500">
          Debe <a href="#" onclick="app.openLoginModal(); return false;" class="text-blue-400 hover:underline">iniciar sesión</a> para dejar un comentario y valoración.
        </div>
      `;
    }

    return `
      <form onsubmit="app.submitComment(event, ${writingId})" class="flex flex-col gap-3 mt-2 border-t border-gray-800/40 pt-4">
        <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <span class="text-xs font-semibold text-gray-300">Añadir tu valoración:</span>
          <!-- Rating stars -->
          <div class="flex items-center gap-1 text-lg text-gray-600" id="rating-stars-${writingId}">
            ${[1,2,3,4,5].map(num => `
              <i class="fa-solid fa-star cursor-pointer hover:text-amber-400 transition" onclick="app.setRatingValue(${writingId}, ${num})"></i>
            `).join('')}
            <input type="hidden" id="rating-value-${writingId}" value="">
          </div>
        </div>

        <div class="flex gap-2">
          <input 
            id="comment-input-${writingId}"
            type="text" 
            placeholder="Escribe tu comentario..." 
            required 
            class="flex-1 px-3 py-2 rounded-lg bg-gray-900 border border-gray-800 text-gray-200 placeholder-gray-500 focus:outline-none focus:border-blue-500 text-sm"
          >
          <button type="submit" class="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-medium text-sm transition duration-200 flex items-center justify-center gap-1">
            <i class="fa-solid fa-paper-plane"></i>
          </button>
        </div>
      </form>
    `;
  }

  setRatingValue(writingId, rating) {
    const input = document.getElementById(`rating-value-${writingId}`);
    input.value = rating;

    const starContainer = document.getElementById(`rating-stars-${writingId}`);
    const stars = starContainer.querySelectorAll('i');
    
    stars.forEach((star, index) => {
      if (index < rating) {
        star.classList.remove('text-gray-600');
        star.classList.add('text-amber-400');
      } else {
        star.classList.remove('text-amber-400');
        star.classList.add('text-gray-600');
      }
    });
  }

  async loadComments(writingId) {
    const listContainer = document.getElementById(`comments-list-${writingId}`);
    listContainer.innerHTML = `<span class="text-xs text-gray-500"><i class="fa-solid fa-spinner fa-spin mr-1"></i>Cargando...</span>`;

    try {
      const response = await fetch(`${this.apiBase}/writings/${writingId}/comments`);
      if (!response.ok) throw new Error();
      
      const comments = await response.json();
      this.activeComments[writingId] = comments;
      this.renderCommentsList(writingId);
    } catch {
      listContainer.innerHTML = `<span class="text-xs text-red-400"><i class="fa-solid fa-circle-exclamation mr-1"></i>Error al cargar comentarios</span>`;
    }
  }

  renderCommentsList(writingId) {
    const listContainer = document.getElementById(`comments-list-${writingId}`);
    const comments = this.activeComments[writingId] || [];

    if (comments.length === 0) {
      listContainer.innerHTML = `<span class="text-xs text-gray-500 italic">No hay comentarios aún. ¡Sé el primero en comentar!</span>`;
      return;
    }

    listContainer.innerHTML = comments.map(c => {
      const dateStr = new Date(c.created_at).toLocaleDateString('es-ES', {
        month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
      });

      const stars = c.rating 
        ? `<div class="flex items-center gap-0.5 text-xs text-amber-400">${Array.from({length: c.rating}).map(() => '<i class="fa-solid fa-star"></i>').join('')}</div>`
        : '';

      const canDelete = this.user && (this.user.role === 'admin' || this.user.id === c.usuario_id);
      
      const deleteButton = canDelete
        ? `<button onclick="app.deleteComment(${writingId}, ${c.id})" class="text-xs text-red-500 hover:text-red-400 transition duration-150">
            <i class="fa-regular fa-trash-can"></i>
           </button>`
        : '';

      return `
        <div class="flex flex-col gap-1.5 p-3 rounded-xl bg-gray-900/40 border border-gray-800/40">
          <div class="flex items-center justify-between gap-3">
            <div class="flex items-center gap-2">
              <span class="text-xs font-bold text-gray-300">${c.usuario_name || 'Usuario'}</span>
              ${stars}
            </div>
            <div class="flex items-center gap-2 text-[10px] text-gray-500">
              <span>${dateStr}</span>
              ${deleteButton}
            </div>
          </div>
          <p class="text-xs sm:text-sm text-gray-300">${c.content}</p>
        </div>
      `;
    }).join('');
  }

  async submitComment(event, writingId) {
    event.preventDefault();
    const commentInput = document.getElementById(`comment-input-${writingId}`);
    const ratingInput = document.getElementById(`rating-value-${writingId}`);

    const content = commentInput.value;
    const rating = ratingInput.value ? parseInt(ratingInput.value) : null;

    try {
      const response = await fetch(`${this.apiBase}/writings/${writingId}/comments`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.token}`
        },
        body: JSON.stringify({ content, rating })
      });

      if (!response.ok) throw new Error('Error al publicar comentario');

      commentInput.value = '';
      ratingInput.value = '';
      
      // Reload comments
      await this.loadComments(writingId);
    } catch (err) {
      alert(err.message);
    }
  }

  async deleteComment(writingId, commentId) {
    if (!confirm('¿Está seguro de que desea eliminar este comentario?')) return;

    try {
      const response = await fetch(`${this.apiBase}/comments/${commentId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${this.token}` }
      });

      if (!response.ok) throw new Error('No se pudo eliminar el comentario');

      await this.loadComments(writingId);
    } catch (err) {
      alert(err.message);
    }
  }

  // Writing Form Actions (Admins)
  async saveWriting(event) {
    event.preventDefault();
    const id = document.getElementById('writing-id').value;
    const title = document.getElementById('w-title').value;
    const content = document.getElementById('w-content').value;
    const status = document.getElementById('w-status').value;
    const tagsStr = document.getElementById('w-tags').value;
    
    // Parse tags by comma
    const tags = tagsStr.split(',')
      .map(t => t.trim())
      .filter(t => t.length > 0);

    const payload = { title, content, status, tags };

    const url = id 
      ? `${this.apiBase}/writings/${id}`
      : `${this.apiBase}/writings/`;

    const method = id ? 'PUT' : 'POST';

    try {
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.token}`
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) throw new Error('Error al guardar el escrito');

      // Reset form
      this.cancelEdit();
      this.fetchWritings();
    } catch (err) {
      alert(err.message);
    }
  }

  async editWriting(id) {
    try {
      const response = await fetch(`${this.apiBase}/writings/${id}`);
      if (!response.ok) throw new Error();
      
      const w = await response.json();
      
      document.getElementById('writing-id').value = w.id;
      document.getElementById('w-title').value = w.title;
      document.getElementById('w-content').value = w.content;
      document.getElementById('w-status').value = w.status;
      document.getElementById('w-tags').value = w.tags ? w.tags.join(', ') : '';

      document.getElementById('editor-title').textContent = 'Editar Escrito';
      document.getElementById('cancel-edit-btn').classList.remove('hidden');
      
      // Scroll to form on mobile
      document.getElementById('admin-panel').scrollIntoView({ behavior: 'smooth' });
    } catch {
      alert('Error al cargar el escrito para editar');
    }
  }

  cancelEdit() {
    document.getElementById('writing-id').value = '';
    document.getElementById('w-title').value = '';
    document.getElementById('w-content').value = '';
    document.getElementById('w-status').value = 'borrador';
    document.getElementById('w-tags').value = '';

    document.getElementById('editor-title').textContent = 'Nuevo Escrito';
    document.getElementById('cancel-edit-btn').classList.add('hidden');
  }

  async deleteWriting(id) {
    if (!confirm('¿Está seguro de que desea eliminar este escrito y todos sus comentarios?')) return;

    try {
      const response = await fetch(`${this.apiBase}/writings/${id}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${this.token}` }
      });

      if (!response.ok) throw new Error('Error al eliminar escrito');
      
      this.fetchWritings();
    } catch (err) {
      alert(err.message);
    }
  }

  // Filtering and Searching
  changeFeedFilter(status) {
    this.currentStatusFilter = status;
    this.searchQuery = '';
    
    // Clear search inputs
    document.getElementById('search-input').value = '';
    document.getElementById('search-input-mobile').value = '';

    // Style filter buttons
    const btns = {
      '': document.getElementById('filter-all'),
      'publicado': document.getElementById('filter-publicados'),
      'borrador': document.getElementById('filter-borradores')
    };

    Object.keys(btns).forEach(key => {
      const btn = btns[key];
      if (!btn) return;
      if (key === status) {
        btn.className = 'px-3 py-1.5 rounded-lg bg-blue-600 text-white shadow shadow-blue-500/10 transition';
      } else {
        btn.className = 'px-3 py-1.5 rounded-lg bg-gray-900 border border-gray-800 text-gray-400 hover:text-gray-200 transition';
      }
    });

    this.fetchWritings();
  }

  handleSearch(event) {
    this.searchQuery = event.target.value.trim();
    
    // Sync inputs
    document.getElementById('search-input').value = this.searchQuery;
    document.getElementById('search-input-mobile').value = this.searchQuery;

    // Debounce search (300ms)
    clearTimeout(this.searchTimeout);
    this.searchTimeout = setTimeout(() => {
      // Clear status filter style
      const btns = [
        document.getElementById('filter-all'),
        document.getElementById('filter-publicados'),
        document.getElementById('filter-borradores')
      ];
      btns.forEach(btn => {
        if (btn) btn.className = 'px-3 py-1.5 rounded-lg bg-gray-900 border border-gray-800 text-gray-400 hover:text-gray-200 transition';
      });
      
      this.fetchWritings();
    }, 300);
  }

  searchTag(tag) {
    this.searchQuery = tag;
    document.getElementById('search-input').value = tag;
    document.getElementById('search-input-mobile').value = tag;
    this.fetchWritings();
  }

  resetFeed() {
    this.changeFeedFilter(this.user && this.user.role === 'admin' ? '' : 'publicado');
  }
}

// Instantiate global app
window.app = new SendaApp();
