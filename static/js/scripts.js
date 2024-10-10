document.addEventListener('DOMContentLoaded', function() {
    const spinner = document.getElementById('spinner');
    const myTab = document.getElementById('myTab');
    const myTabContent = document.getElementById('myTabContent');
    const myFileLink = document.getElementById('myFileLink');

    // Fonction pour récupérer les données de la vue transits_data
    async function fetchData() {
        try {
            const response = await fetch('data'); // Appel à la vue transits_data
            const data = await response.json();
            console.log(data)

            // Cacher le spinner après le chargement
            spinner.style.display = 'none';

            // Générer les onglets et les contenus
            renderTabs(data.data);

            //Générer le lien de téléchargement du fichier pour le casier
            renderFileLink(data.docs_pour_Marne,data.file_url)
        } catch (error) {
            console.error('Erreur lors de la récupération des données :', error);
        }
    }

    // Fonction pour générer les onglets de bibliothèques de retrait
    function renderTabs(resas) {
        resas.forEach((entry, index) => {
            // Créer l'onglet pour chaque bibliothèque de retrait
            const tab = document.createElement('li');
            tab.className = 'nav-item';
            tab.innerHTML = `
                <button class="nav-link ${index === 0 ? 'active' : ''} btn-lg" id="tab-${index + 1}" 
                        data-bs-toggle="tab" data-bs-target="#tab-content-${index + 1}" 
                        type="button" role="tab" aria-controls="tab-content-${index + 1}" aria-selected="${index === 0}">
                    ${entry.bibliotheque_retrait} <span class="badge badge-pill badge-light">${entry.nombre_doc_a_prendre_en_charge}</span>
                </button>
            `;
            myTab.appendChild(tab);

            // Générer le contenu correspondant
            renderTabContent(entry, index);
        });
    }
    //Fonction pour modifier le bouton le de téléchargement du fichier d'alimentation de l'automate
    function renderFileLink(docs_pour_Marne,url) {
        const fileLink = document.createElement('a');
        if (docs_pour_Marne){
            fileLink.className = `btn btn-primary btn-lg`;
            fileLink.setAttribute("role","button");
            fileLink.href = url
            fileLink.textContent = "Télécharger le fichier pour l'alimentation du casier à la BU Marne"
        }
        else{
            fileLink.className = `btn btn-light btn-lg disabled`;
            fileLink.setAttribute("role","button");
            fileLink.setAttribute("aria-disabled","true");
            fileLink.href = ""
            fileLink.textContent = "Pas de document pour la BU Marne"

        }
        myFileLink.appendChild(fileLink)
    }
    // Fonction pour générer le contenu des onglets
    function renderTabContent(entry, index) {
        const tabContent = document.createElement('div');
        tabContent.className = `tab-pane fade ${index === 0 ? 'show active' : ''}`;
        tabContent.id = `tab-content-${index + 1}`;
        tabContent.role = 'tabpanel';
        tabContent.ariaLabelledby = `tab-${index + 1}`;

        let destinationTabs = '';
        let destinationContent = '';

        // Générer les sous-onglets pour les bibliothèques de destination
        entry.bibliotheque_destination.forEach((destination, i) => {
            destinationTabs += `
                <li class="nav-item" role="presentation">
                    <button class="nav-link ${i === 0 ? 'active' : ''}" 
                            id="pills-${i + 1}-${index + 1}" data-bs-toggle="pill" 
                            data-bs-target="#pills-content-${i + 1}-${index + 1}" 
                            type="button" role="tab" 
                            aria-controls="pills-content-${i + 1}-${index + 1}" aria-selected="${i === 0}">
                        ${destination.nom} <span class="badge badge-pill badge-light">${destination.items.length}</span>
                    </button>
                </li>
            `;

            // Générer le contenu des items
            let itemsHTML = '';
            destination.items.forEach(item => {
                itemsHTML += `
                    <div class="col-md-6 mb-4">
                        <div class="card h-100 ${item.type_de_demande}">
                            <div class="card-body">
                                <h5 class="card-title">${item.titre}</h5>
                                <p class="card-text"><strong>Code barre :</strong> ${item.cb}</p>
                                <span class="badge badge-pill badge-light position-absolute top-0 end-0">${item.type_de_demande}</span>
                            </div>
                        </div>
                    </div>
                `;
            });

            destinationContent += `
                <div class="tab-pane fade ${i === 0 ? 'show active' : ''}" 
                     id="pills-content-${i + 1}-${index + 1}" role="tabpanel" aria-labelledby="pills-${i + 1}-${index + 1}">
                    <h3 class="mb-4">Bibliothèque de destination : ${destination.nom}</h3>
                    <div class="row">${itemsHTML}</div>
                </div>
            `;
        });

        // Ajouter les sous-onglets et les items au contenu
        tabContent.innerHTML = `
            <h2 class="mb-4">Bibliothèque de retrait : ${entry.bibliotheque_retrait}</h2>
            <ul class="nav nav-pills mb-3" id="pills-tab-${index + 1}" role="tablist">
                ${destinationTabs}
            </ul>
            <div class="tab-content" id="pills-tabContent-${index + 1}">
                ${destinationContent}
            </div>
        `;

        myTabContent.appendChild(tabContent);
    }

    // Appel de la fonction fetchData pour récupérer et afficher les données
    fetchData();
});
