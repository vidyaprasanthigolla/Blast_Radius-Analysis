document.addEventListener('DOMContentLoaded', () => {
    let cy = cytoscape({
        container: document.getElementById('cy'),
        style: [
            {
                selector: 'node',
                style: {
                    'background-color': '#8b949e',
                    'label': 'data(label)',
                    'color': '#c9d1d9',
                    'font-size': '12px',
                    'text-valign': 'bottom',
                    'text-halign': 'center',
                    'text-margin-y': '6px',
                    'width': '30px',
                    'height': '30px'
                }
            },
            {
                selector: 'edge',
                style: {
                    'width': 2,
                    'line-color': '#30363d',
                    'target-arrow-color': '#30363d',
                    'target-arrow-shape': 'triangle',
                    'curve-style': 'bezier',
                    'label': 'data(label)',
                    'font-size': '10px',
                    'color': '#8b949e',
                    'text-rotation': 'autorotate',
                    'text-margin-y': '-10px'
                }
            },
            {
                selector: '.modified',
                style: {
                    'background-color': '#f85149',
                    'width': '40px',
                    'height': '40px',
                    'border-width': '4px',
                    'border-color': 'rgba(248, 81, 73, 0.3)'
                }
            },
            {
                selector: '.direct-impact',
                style: { 'background-color': '#d29922' }
            },
            {
                selector: '.indirect-impact',
                style: { 'background-color': '#8957e5' }
            },
            {
                selector: '.impact-edge',
                style: {
                    'line-color': '#58a6ff',
                    'target-arrow-color': '#58a6ff',
                    'width': 3
                }
            }
        ]
    });

    const analyzeBtn = document.getElementById('analyzeBtn');
    const formCard = document.getElementById('formCard');
    const resultsCard = document.getElementById('resultsCard');
    const reportContent = document.getElementById('reportContent');
    const impactCount = document.getElementById('impactCount');
    const emptyState = document.getElementById('emptyState');
    const shareBox = document.getElementById('shareBox');
    const shareLink = document.getElementById('shareLink');
    const copyBtn = document.getElementById('copyBtn');
    const subtitleText = document.getElementById('subtitleText');

    // Check if we are viewing a shared report natively
    const bodyReportId = document.body.getAttribute('data-report-id');
    if (bodyReportId) {
        formCard.style.display = 'none';
        subtitleText.textContent = `Viewing Shared Report: ${bodyReportId}`;
        fetchReportData(bodyReportId);
    }

    if (analyzeBtn) {
        analyzeBtn.addEventListener('click', async () => {
            const repoPath = document.getElementById('repoPath').value;
            const nodeId = document.getElementById('nodeId').value;
            const changeIntent = document.getElementById('changeIntent').value;

            if (!repoPath || !nodeId) {
                alert('Please provide all details.');
                return;
            }

            analyzeBtn.disabled = true;
            document.getElementById('btnSpinner').style.display = 'block';

            try {
                const res = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        repo_path: repoPath,
                        change_intent: changeIntent,
                        changed_node_id: nodeId
                    })
                });

                const data = await res.json();
                if (!res.ok) throw new Error(data.error || 'Failed to analyze');

                renderData(data);

                // Setup share link
                const link = `${window.location.origin}/report/${data.report_id}`;
                shareLink.value = link;
                shareBox.style.display = 'block';

            } catch (err) {
                alert('Error: ' + err.message);
            } finally {
                analyzeBtn.disabled = false;
                document.getElementById('btnSpinner').style.display = 'none';
            }
        });
    }

    copyBtn.addEventListener('click', () => {
        shareLink.select();
        document.execCommand('copy');
        copyBtn.textContent = 'Copied!';
        setTimeout(() => copyBtn.textContent = 'Copy', 2000);
    });

    async function fetchReportData(reportId) {
        try {
            emptyState.textContent = 'Loading shared report...';
            const res = await fetch(`/api/report/${reportId}`);
            if (!res.ok) throw new Error('Report not found');
            const data = await res.json();
            renderData(data);
        } catch (err) {
            emptyState.textContent = err.message;
            alert(err.message);
        }
    }

    function renderData(data) {
        emptyState.style.display = 'none';

        const nodes = data.graph_elements.filter(e => e.data.id && !e.data.source).map(n => ({ data: n.data }));
        const edges = data.graph_elements.filter(e => e.data.source && e.data.target).map(e => ({ data: e.data }));

        cy.elements().remove();
        cy.add([...nodes, ...edges]);

        cy.layout({
            name: 'cose',
            animate: true,
            idealEdgeLength: 100,
            nodeOverlap: 20
        }).run();

        const impacts = data.impact_analysis.impacts;
        impactCount.textContent = `${data.impact_analysis.total_impacted} affected components`;
        reportContent.innerHTML = '';

        const subgraphIds = new Set(data.impact_analysis.subgraph_nodes);

        impacts.forEach(impact => {
            const html = `
                <div class="impact-item level-${impact.impact_level}">
                    <h4>${impact.id}</h4>
                    <div class="impact-meta">
                        <span>⚡ ${impact.impact_level}</span>
                        ${impact.category ? `<span>| 🗂️ ${impact.category}</span>` : ''}
                    </div>
                    <p class="impact-desc">${impact.explanation}</p>
                </div>
            `;
            reportContent.insertAdjacentHTML('beforeend', html);

            const cyNode = cy.getElementById(impact.id);
            if (cyNode) {
                if (impact.impact_level === 'Changed') cyNode.addClass('modified');
                else if (impact.impact_level === 'Direct') cyNode.addClass('direct-impact');
                else cyNode.addClass('indirect-impact');
            }
        });

        cy.edges().forEach(edge => {
            if (subgraphIds.has(edge.source().id()) && subgraphIds.has(edge.target().id())) {
                edge.addClass('impact-edge');
            }
        });

        resultsCard.style.display = 'block';
    }
});
