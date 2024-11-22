// import React, { useState } from 'react';
// import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
// import CreateModel from './pages/models/createModel/CreateModel';
// import HomePage from './pages/home/home';
// import NavBar from './components/nav/NavBar';
// import Login from './pages/login/login';
// import Dashboard from './pages/dashboard/dashboard';
// import Games from './pages/games/games';
// import ModelsHome from './pages/models/modelsHome/modelsHome';
// import PrivateRoute from './components/auth/PrivateRoute';
// import { AuthProvider } from './components/auth/AuthContext';
// import './App.css';
// import EditModel from './pages/models/editModel/EditModel';

// function App() {
//   const [sideNavOpen, setSideNavOpen] = useState(false);

//   const toggleSideNav = () => {
//     setSideNavOpen(!sideNavOpen);
//   };

//   return (
//     <AuthProvider>
//       <Router>
//         <NavBar sideNavOpen={sideNavOpen} toggleSideNav={toggleSideNav} />
//         <Routes>
//           <Route path="/" element={<HomePage />} />
//           <Route path="/signin" element={<Login />} />
//           <Route path="/create-model" element={<CreateModel />}/>
//           {/* Dashboard */}
//           <Route exact path="/:user_id/dashboard" element={<PrivateRoute />}>
//             <Route exact path= "/:user_id/dashboard" element={<Dashboard sideNavOpen={sideNavOpen} />} />
//           </Route>
//           {/* Games */}
//           <Route exact path="/:user_id/:model_id/games" element={<PrivateRoute />}>
//             <Route exact path= "/:user_id/:model_id/games" element={<Games />} />
//           </Route>
//           {/* Models Home */}
//           <Route exact path="/:user_id/models" element={<PrivateRoute />}>
//             <Route exact path= "/:user_id/models" element={<ModelsHome />} />
//           </Route>
//           {/* CFB Model Creator */}
//           <Route exact path="/:user_id/create-model" element={<PrivateRoute />}>
//             <Route exact path= "/:user_id/create-model" element={<CreateModel />} />
//           </Route>
//           {/* CFB Model Editor */}
//           <Route exact path="/:user_id/model/:modelId" element={<PrivateRoute />}>
//             <Route exact path= "/:user_id/model/:modelId" element={<EditModel />} />
//           </Route>
//           {/* Add other routes here if needed */}
//         </Routes>
//       </Router>
//     </AuthProvider>
//   );
// }

// export default App;



import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import CreateModel from './pages/models/createModel/CreateModel';
import HomePage from './pages/home/home';
import NavBar1 from './components/nav/NavBar1';
import Login from './pages/login/login';
import Dashboard from './pages/dashboard/dashboard';
import Games from './pages/games/games';
import ModelsHome from './pages/models/modelsHome/modelsHome';
import PrivateRoute from './components/auth/PrivateRoute';
import TestAccuracy from './pages/models/testModel/TestAccuracy';
import LiveAccuracy from './pages/models/liveAccuracy/liveAccuracy';
import { AuthProvider } from './components/auth/AuthContext';
import './App.css';
import EditModel from './pages/models/editModel/EditModel';

function App() {

  return (
    <AuthProvider>
      <Router>
        <NavBar1>
          <Routes>
            <Route path="/" element={<HomePage />}/>
            <Route path="/signin" element={<Login />} />
            <Route path="/create-model" element={<CreateModel />}/>
            {/* Dashboard */}
            <Route exact path="/:user_id/dashboard" element={<PrivateRoute />}>
              <Route exact path= "/:user_id/dashboard" element={<Dashboard />} />
            </Route>
            {/* Games */}
            <Route exact path="/:user_id/:model_id/games" element={<PrivateRoute />}>
              <Route exact path= "/:user_id/:model_id/games" element={<Games />} />
            </Route>

            {/* Test model on last years games */}
            <Route exact path="/:user_id/:model_id/test-accuracy" element={<PrivateRoute />}>
              <Route exact path= "/:user_id/:model_id/test-accuracy" element={<TestAccuracy />} />
            </Route>

            {/* Test model on the bets a model has made */}
            <Route exact path="/:user_id/:model_id/live-accuracy" element={<PrivateRoute />}>
              <Route exact path= "/:user_id/:model_id/live-accuracy" element={<LiveAccuracy />} />
            </Route>

            {/* Models Home */}
            <Route exact path="/:user_id/models" element={<PrivateRoute />}>
              <Route exact path= "/:user_id/models" element={<ModelsHome />} />
            </Route>
            {/* CFB Model Creator */}
            <Route exact path="/:user_id/create-model" element={<PrivateRoute />}>
              <Route exact path= "/:user_id/create-model" element={<CreateModel />} />
            </Route>
            {/* CFB Model Editor */}
            <Route exact path="/:user_id/model/:modelId" element={<PrivateRoute />}>
              <Route exact path= "/:user_id/model/:modelId" element={<EditModel />} />
            </Route>
            {/* Add other routes here if needed */}
          </Routes>
        </NavBar1>
        
      </Router>
    </AuthProvider>
  );
}

export default App;
