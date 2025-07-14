// SGFP - Sistema de Gestão Financeira Pessoal
// JavaScript principal

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Inicializar popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Formatação de valores monetários
    window.formatCurrency = function(value) {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(value);
    };

    // Formatação de datas
    window.formatDate = function(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('pt-BR');
    };

    // Função para mostrar loading
    window.showLoading = function(element) {
        if (element) {
            element.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Carregando...';
            element.disabled = true;
        }
    };

    // Função para esconder loading
    window.hideLoading = function(element, originalText) {
        if (element) {
            element.innerHTML = originalText;
            element.disabled = false;
        }
    };

    // Função para mostrar notificações
    window.showNotification = function(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const container = document.querySelector('.container-fluid') || document.querySelector('.container');
        if (container) {
            container.insertBefore(alertDiv, container.firstChild);
            
            // Auto-remover após 5 segundos
            setTimeout(() => {
                if (alertDiv.parentNode) {
                    alertDiv.remove();
                }
            }, 5000);
        }
    };

    // Função para confirmar ações
    window.confirmAction = function(message, callback) {
        if (confirm(message)) {
            callback();
        }
    };

    // Função para validar formulários
    window.validateForm = function(formElement) {
        const inputs = formElement.querySelectorAll('input[required], select[required], textarea[required]');
        let isValid = true;

        inputs.forEach(input => {
            if (!input.value.trim()) {
                input.classList.add('is-invalid');
                isValid = false;
            } else {
                input.classList.remove('is-invalid');
            }
        });

        return isValid;
    };

    // Função para limpar formulários
    window.clearForm = function(formElement) {
        const inputs = formElement.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.value = '';
            input.classList.remove('is-invalid');
        });
    };

    // Função para atualizar saldo da conta via AJAX
    window.updateAccountBalance = function(accountId) {
        fetch(`/api/conta/${accountId}/saldo/`)
            .then(response => response.json())
            .then(data => {
                const balanceElement = document.querySelector(`[data-account-id="${accountId}"]`);
                if (balanceElement) {
                    balanceElement.textContent = formatCurrency(data.saldo);
                    balanceElement.className = data.saldo >= 0 ? 'text-success' : 'text-danger';
                }
            })
            .catch(error => {
                console.error('Erro ao atualizar saldo:', error);
            });
    };

    // Função para exportar dados
    window.exportData = function(data, filename, type = 'csv') {
        let content = '';
        let mimeType = '';

        if (type === 'csv') {
            content = convertToCSV(data);
            mimeType = 'text/csv';
        } else if (type === 'json') {
            content = JSON.stringify(data, null, 2);
            mimeType = 'application/json';
        }

        const blob = new Blob([content], { type: mimeType });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        window.URL.revokeObjectURL(url);
    };

    // Função para converter dados para CSV
    function convertToCSV(data) {
        if (!data || data.length === 0) return '';

        const headers = Object.keys(data[0]);
        const csvContent = [
            headers.join(','),
            ...data.map(row => headers.map(header => `"${row[header]}"`).join(','))
        ].join('\n');

        return csvContent;
    }

    // Função para filtrar tabelas
    window.filterTable = function(tableId, searchTerm) {
        const table = document.getElementById(tableId);
        if (!table) return;

        const rows = table.querySelectorAll('tbody tr');
        const term = searchTerm.toLowerCase();

        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(term) ? '' : 'none';
        });
    };

    // Função para ordenar tabelas
    window.sortTable = function(tableId, columnIndex, type = 'string') {
        const table = document.getElementById(tableId);
        if (!table) return;

        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));

        rows.sort((a, b) => {
            let aValue = a.cells[columnIndex].textContent.trim();
            let bValue = b.cells[columnIndex].textContent.trim();

            if (type === 'number') {
                aValue = parseFloat(aValue.replace(/[^\d.-]/g, '')) || 0;
                bValue = parseFloat(bValue.replace(/[^\d.-]/g, '')) || 0;
            } else if (type === 'date') {
                aValue = new Date(aValue.split('/').reverse().join('-'));
                bValue = new Date(bValue.split('/').reverse().join('-'));
            }

            if (aValue < bValue) return -1;
            if (aValue > bValue) return 1;
            return 0;
        });

        // Limpar tbody e adicionar linhas ordenadas
        tbody.innerHTML = '';
        rows.forEach(row => tbody.appendChild(row));
    };

    // Função para fazer backup dos dados
    window.backupData = function() {
        showNotification('Iniciando backup dos dados...', 'info');
        
        fetch('/api/backup/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('Backup realizado com sucesso!', 'success');
            } else {
                showNotification('Erro ao realizar backup: ' + data.error, 'danger');
            }
        })
        .catch(error => {
            showNotification('Erro ao realizar backup: ' + error.message, 'danger');
        });
    };

    // Função para obter cookie CSRF
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Event listeners para formulários
    document.addEventListener('submit', function(e) {
        const form = e.target;
        if (form.classList.contains('needs-validation')) {
            if (!validateForm(form)) {
                e.preventDefault();
                e.stopPropagation();
            }
        }
    });

    // Event listeners para botões de loading
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('btn-loading')) {
            const originalText = e.target.innerHTML;
            showLoading(e.target);
            
            // Simular operação assíncrona
            setTimeout(() => {
                hideLoading(e.target, originalText);
            }, 2000);
        }
    });

    // Event listeners para filtros de tabela
    document.addEventListener('input', function(e) {
        if (e.target.classList.contains('table-filter')) {
            const tableId = e.target.getAttribute('data-table');
            const searchTerm = e.target.value;
            filterTable(tableId, searchTerm);
        }
    });

    // Event listeners para ordenação de tabela
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('sortable')) {
            const tableId = e.target.closest('table').id;
            const columnIndex = Array.from(e.target.parentNode.children).indexOf(e.target);
            const dataType = e.target.getAttribute('data-type') || 'string';
            sortTable(tableId, columnIndex, dataType);
        }
    });

    // --- TEMA GLOBAL E SINCRONIZAÇÃO DOS SELETORES ---
    const THEME_KEY = 'sgfp_theme';
    const themeOptions = [
        'corona-dark',
        'vanta-dark',
        'staradmin-color',
        'futureui-color',
        'material-light',
        'celestial-light'
    ];

    function applyTheme(theme) {
        document.body.classList.remove(...themeOptions);
        if (themeOptions.includes(theme)) {
            document.body.classList.add(theme);
        }
    }

    function syncThemeSelectors(theme) {
        const configSelector = document.getElementById('theme-selector-config');
        const loginSelector = document.getElementById('theme-selector-login');
        if (configSelector) configSelector.value = theme;
        if (loginSelector) loginSelector.value = theme;
    }

    function setupThemeSelector(selectorId) {
        const selector = document.getElementById(selectorId);
        if (selector) {
            selector.addEventListener('change', function() {
                const selectedTheme = this.value;
                // Se o usuário está autenticado (tema_usuario presente no body), submeter o formulário
                if (document.body.className && themeOptions.includes(document.body.className)) {
                    // Se estiver na página de configurações, submeter o formulário
                    const configForm = document.getElementById('configForm');
                    if (configForm) {
                        // Atualiza o campo real do formulário
                        const formField = document.getElementById('id_dashboard_tema');
                        if (formField) formField.value = selectedTheme;
                        configForm.submit();
                    }
                } else {
                    // Usuário anônimo: salvar no localStorage e aplicar
                    localStorage.setItem(THEME_KEY, selectedTheme);
                    applyTheme(selectedTheme);
                    syncThemeSelectors(selectedTheme);
                }
            });
        }
    }

    // Ao carregar a página
    (function() {
        // Se o usuário está autenticado, não sobrescrever o tema do backend
        if (document.body.className && themeOptions.includes(document.body.className)) {
            syncThemeSelectors(document.body.className);
        } else {
            // Usuário anônimo: aplicar tema do localStorage
            const savedTheme = localStorage.getItem(THEME_KEY) || 'corona-dark';
            applyTheme(savedTheme);
            syncThemeSelectors(savedTheme);
        }
        setupThemeSelector('theme-selector-config');
        setupThemeSelector('theme-selector-login');
    })();
    // --- FIM TEMA GLOBAL ---

    // Função para inicializar tooltips do sidebar
    function initSidebarTooltips() {
        const sidebar = document.getElementById('sidebar');
        const isCollapsed = sidebar.classList.contains('collapsed');
        const iconEls = sidebar.querySelectorAll('.sidebar-icon');
        iconEls.forEach(function(icon) {
            if (isCollapsed) {
                icon.setAttribute('data-bs-toggle', 'tooltip');
                icon.setAttribute('data-bs-placement', 'right');
            } else {
                icon.removeAttribute('data-bs-toggle');
                icon.removeAttribute('data-bs-placement');
            }
        });
        if (isCollapsed) {
            var tooltipTriggerList = [].slice.call(document.querySelectorAll('.sidebar-icon[data-bs-toggle="tooltip"]'));
            tooltipTriggerList.forEach(function (tooltipTriggerEl) {
                new bootstrap.Tooltip(tooltipTriggerEl);
            });
        } else {
            var tooltips = document.querySelectorAll('.sidebar-icon');
            tooltips.forEach(function (el) {
                if (el._tooltip) { el._tooltip.dispose(); }
            });
        }
    }

    function toggleSidebar() {
        const sidebar = document.getElementById('sidebar');
        const mainContent = document.querySelector('.main-content');
        const overlay = document.getElementById('sidebarOverlay');
        if (window.innerWidth <= 991) {
            sidebar.classList.toggle('show');
            overlay.classList.toggle('show');
        } else {
            sidebar.classList.toggle('collapsed');
            mainContent.classList.toggle('sidebar-collapsed');
            if (sidebar.classList.contains('collapsed')) {
                localStorage.setItem('sidebar-collapsed', '1');
            } else {
                localStorage.removeItem('sidebar-collapsed');
            }
        }
        setTimeout(initSidebarTooltips, 350);
    }

    // Adicionar evento para atualizar tooltips do sidebar quando o menu lateral muda de estado
    document.addEventListener('DOMContentLoaded', function() {
        const sidebar = document.getElementById('sidebar');
        const mainContent = document.querySelector('.main-content');
        // Sempre inicia retraído, a menos que o usuário tenha expandido
        if (localStorage.getItem('sidebar-collapsed') !== null) {
            sidebar.classList.add('collapsed');
            mainContent.classList.add('sidebar-collapsed');
        }
        // Acessibilidade: navegação por teclado
        document.querySelectorAll('#sidebarMenu .nav-link').forEach(link => {
            link.addEventListener('keydown', function(e) {
                if (e.key === 'ArrowDown') {
                    e.preventDefault();
                    const next = this.parentElement.nextElementSibling;
                    if (next) next.querySelector('.nav-link').focus();
                } else if (e.key === 'ArrowUp') {
                    e.preventDefault();
                    const prev = this.parentElement.previousElementSibling;
                    if (prev) prev.querySelector('.nav-link').focus();
                }
            });
        });
        initSidebarTooltips();
    });

    console.log('SGFP JavaScript carregado com sucesso!');
}); 