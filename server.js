import express from 'express';
import { engine } from 'express-handlebars';
import fileUpload from 'express-fileupload';
import bodyParser from 'body-parser';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const port = 3000;

// Middleware
app.use(bodyParser.urlencoded({ extended: true }));
app.use(fileUpload());
app.use(express.static('static'));
app.use('/static/images', express.static('static/images'));

// Handlebars setup
app.engine('handlebars', engine());
app.set('view engine', 'handlebars');
app.set('views', './templates');

// Ensure images directory exists
if (!fs.existsSync('./static/images')) {
  fs.mkdirSync('./static/images', { recursive: true });
}

// Routes
app.get('/', (req, res) => {
  res.render('index');
});

app.get('/browse', (req, res) => {
  let items = [];
  if (fs.existsSync('items.json')) {
    items = JSON.parse(fs.readFileSync('items.json', 'utf8'));
  }
  res.render('browse', { items });
});

app.get('/signup', (req, res) => {
  res.render('signup');
});

app.post('/signup', (req, res) => {
  const userData = {
    name: req.body.name,
    email: req.body.email,
    address: req.body.address,
    phone: req.body.phone,
    payment: req.body.payment,
    account_type: req.body.account_type
  };

  let users = [];
  if (fs.existsSync('users.json')) {
    users = JSON.parse(fs.readFileSync('users.json', 'utf8'));
  }

  users.push(userData);
  fs.writeFileSync('users.json', JSON.stringify(users, null, 4));

  if (userData.account_type === 'Personal Seller') {
    res.redirect(`/personaloption?email=${encodeURIComponent(userData.email)}`);
  } else if (userData.account_type === 'Enterprise Seller') {
    res.redirect('/business-membership');
  } else {
    res.redirect('/');
  }
});

app.get('/personaloption', (req, res) => {
  res.render('personaloption', { email: req.query.email });
});

app.post('/personaloption', (req, res) => {
  const { email, duration, sale_area, miles, shipping } = req.body;
  
  let users = [];
  if (fs.existsSync('users.json')) {
    users = JSON.parse(fs.readFileSync('users.json', 'utf8'));
  }

  users = users.map(user => {
    if (user.email === email) {
      return {
        ...user,
        duration,
        sale_area,
        miles,
        shipping
      };
    }
    return user;
  });

  fs.writeFileSync('users.json', JSON.stringify(users, null, 4));
  res.redirect(`/additems?email=${encodeURIComponent(email)}`);
});

app.get('/additems', (req, res) => {
  res.render('additems', { email: req.query.email });
});

app.post('/additems', (req, res) => {
  if (!req.files || !req.files.image) {
    return res.status(400).send('No image uploaded');
  }

  const { email, item_name, description, price } = req.body;
  const image = req.files.image;
  const image_filename = image.name;

  // Save image
  image.mv(path.join(__dirname, 'static/images', image_filename), err => {
    if (err) return res.status(500).send(err);

    // Save item data
    const itemData = {
      email,
      item_name,
      description,
      price,
      image_filename
    };

    let items = [];
    if (fs.existsSync('items.json')) {
      items = JSON.parse(fs.readFileSync('items.json', 'utf8'));
    }

    items.push(itemData);
    fs.writeFileSync('items.json', JSON.stringify(items, null, 4));

    res.redirect('/browse');
  });
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});