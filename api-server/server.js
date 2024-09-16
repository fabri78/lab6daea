const express = require('express');
const cors = require('cors');
const mongoose = require('mongoose');

// Crear una instancia de Express
const app = express();

// Usar middleware para habilitar CORS
app.use(cors());

// Configuración de body-parser para manejar JSON
app.use(express.json());

// Conectar a MongoDB
mongoose.connect('mongodb+srv://fabricioquispe:Nm8AxHP2aoa3ykd6@movies.3ealn.mongodb.net/movies?retryWrites=true&w=majority', {
    useNewUrlParser: true,
    useUnifiedTopology: true
}).then(() => console.log('Conectado a MongoDB'))
  .catch((err) => console.error('Error conectando a MongoDB:', err));

// Definir el esquema y modelo de películas
const movieSchema = new mongoose.Schema({
    movie_id: String,
    movie_title: String,
    num_votaciones: Number
});

const Movie = mongoose.model('Movie', movieSchema);

// Definir el esquema y modelo de ocupaciones
const occupationSchema = new mongoose.Schema({
    movie_title: String,
    occupation: String,
    num_votaciones_por_ocupacion: Number
});

const Occupation = mongoose.model('Occupation', occupationSchema);

app.get('/', (req, res) => {
    res.send('Servidor funcionando correctamente');
});
// Ruta para obtener las películas más votadas
app.get('/top-movies', async (req, res) => {
    try {
        const topMovies = await Movie.find().sort({ num_votaciones: -1 }).limit(5);
        res.json(topMovies);
    } catch (error) {
        res.status(500).json({ message: 'Error al obtener las películas', error });
    }
});


// Ruta para obtener ocupaciones por película
app.get('/api/occupations', async (req, res) => {
    try {
        const movieTitle = req.query.movie_title;
        if (!movieTitle) {
            return res.status(400).json({ message: 'El título de la película es requerido' });
        }
        const occupations = await Occupation.find({ movie_title: movieTitle });
        res.json(occupations);
    } catch (error) {
        res.status(500).json({ message: 'Error al obtener las ocupaciones', error });
    }
});

// Iniciar el servidor en el puerto 3000
const PORT = 3000;
app.listen(PORT, () => {
    console.log(`Servidor corriendo en http://localhost:${PORT}`);
});
