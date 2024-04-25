import './Styles/Pages.css';
import './Styles/Chat.css'

import { BrowserRouter, Route, Routes } from 'react-router-dom';
import Navbar from './Components/Navbar';
import Home from './Pages/Home';

function App() {
  return (
    <div className="site">
      <BrowserRouter>
            <Navbar/>
              <Routes>
                <Route path="/" element={ <Home/> } />
              </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
