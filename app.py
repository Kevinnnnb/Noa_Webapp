<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Recherche de GIFs</title>
    <style>
        body {
            background-color: pink;
            margin: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: "100vh";
            font-family: "Lucida Console", "Courier New", monospace;
            overflow-x: hidden; /* Empêcher le défilement horizontal */
        }

        .container {
            background-color: white;
            width: 90%;
            max-width: "600px"; 
            padding: 3%;
            border-radius: "20px";
            text-align: center;
            display: flex;
            flex-direction: column;
            align-items: center;
            box-sizing: border-box;
        }

        #gif-container {
            margin-top: "20px";
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
        }

        .gif {
            width: 100%;
            height: auto;
            margin: "10px";
            border-radius: "10px";
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            max-width: "200px";
            cursor: pointer;
        }

        #search-form {
            margin-bottom: "20px";
            display: flex;
            flex-direction: column;
            align-items: center;
            width: 100%;
        }

        #search-input {
            padding: "10px";
            font-size: "16px";
            border: 1px solid #ddd;
            border-radius: "4px";
            margin-bottom: "10px";
            width: 100%;
            box-sizing: border-box;
        }

        button {
            padding: "10px" "15px";
            border: none;
            border-radius: "4px";
            background-color: pink;
            color: white;
            font-size: "16px";
            cursor: pointer;
            margin: "5px";
        }

        button:hover {
            background-color: red;
        }

        @media (min-width: "600px") {
            #search-form {
                flex-direction: row;
            }

            #search-input {
                margin-bottom: 0;
                margin-right: "10px";
                width: auto;
                flex-grow: 1;
            }

            .gif {
                width: auto;
                margin: "10px";
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h3>Rechercher un GIF</h3>
        <form id="search-form" onsubmit="return fetchGifs(event);">
            <input type="text" id="search-input" placeholder="Rechercher un GIF" required />
            <button type="submit">Rechercher</button>
        </form>
        <div id="gif-container"></div>
    </div>

    <script>
        async function fetchGifs(event) {
            event.preventDefault();
            const apiKey = 'L0ShI5mRJUndorPXzD1y7mV5YpJZTU4s';
            const query = document.getElementById('search-input').value;
            const limit = 10;
            const url = `https://api.giphy.com/v1/gifs/search?api_key=${apiKey}&q=${query}&limit=${limit}`;

            try {
                const response = await fetch(url);
                const result = await response.json();
                const gifContainer = document.getElementById('gif-container');
                gifContainer.innerHTML = '';

                result.data.forEach(gif => {
                    const img = document.createElement('img');
                    img.src = gif.images.fixed_height.url;
                    img.alt = gif.title;
                    img.className = 'gif';
                    img.addEventListener('click', () => uploadGif(gif.images.fixed_height.url));
                    gifContainer.appendChild(img);
                });
            } catch (error) {
                console.error('Erreur lors de la récupération des GIFs:', error);
            }
        }

        async function uploadGif(gifUrl) {
            try {
                const response = await fetch(gifUrl);
                const blob = await response.blob();
                const file = new File([blob], 'image.gif', { type: 'image/gif' });
                const formData = new FormData();
                formData.append('img', file);

                const uploadResponse = await fetch('/upload', {
                    method: 'POST',
                    body: formData,
                });

                if (uploadResponse.ok) {
                    console.log('GIF envoyé avec succès');
                } else {
                    console.error('Erreur lors de l\'envoi du GIF:', await uploadResponse.text());
                }
            } catch (error) {
                console.error('Erreur lors de l\'upload du GIF:', error);
            }
        }
    </script>
</body>
</html>
