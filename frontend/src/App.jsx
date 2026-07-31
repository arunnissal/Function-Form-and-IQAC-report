import React, { useContext } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, AuthContext } from './AuthContext';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import NewRequest from './pages/NewRequest';
import MyRequests from './pages/MyRequests';
import ApprovalQueue from './pages/ApprovalQueue';
import EventCalendar from './pages/EventCalendar';
import ManageHalls from './pages/ManageHalls';
import ManageDepartments from './pages/ManageDepartments';
import ManageStaff from './pages/ManageStaff';
import ChangePassword from './pages/ChangePassword';
import EditRequest from './pages/EditRequest';
import ViewRequest from './pages/ViewRequest';

const ProtectedRoute = ({ children, allowedRoles, requireSuperuser }) => {
  const { user, loading } = useContext(AuthContext);
  if (loading) return <div style={{padding: '2rem', textAlign: 'center'}}>Loading application...</div>;
  if (!user) return <Navigate to="/login" replace />;
  if (requireSuperuser && !user.is_superuser && user.role !== 'MANAGEMENT') {
    return <Navigate to="/dashboard" replace />;
  }
  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return <Navigate to="/dashboard" replace />;
  }
  return children;
};

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/dashboard" element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          } />
          <Route path="/new-request" element={
            <ProtectedRoute allowedRoles={['FACULTY', 'HOD']}>
              <NewRequest />
            </ProtectedRoute>
          } />
          <Route path="/edit-request/:id" element={
            <ProtectedRoute allowedRoles={['FACULTY', 'HOD', 'MANAGEMENT', 'PRINCIPAL', 'DEAN_COMPUTING']}>
              <EditRequest />
            </ProtectedRoute>
          } />
          <Route path="/request/:id" element={
            <ProtectedRoute>
              <ViewRequest />
            </ProtectedRoute>
          } />
          <Route path="/my-requests" element={
            <ProtectedRoute>
              <MyRequests />
            </ProtectedRoute>
          } />
          <Route path="/approvals" element={
            <ProtectedRoute>
              <ApprovalQueue />
            </ProtectedRoute>
          } />
          <Route path="/calendar" element={
            <ProtectedRoute>
              <EventCalendar />
            </ProtectedRoute>
          } />
          <Route path="/manage-halls" element={
            <ProtectedRoute requireSuperuser={true}>
              <ManageHalls />
            </ProtectedRoute>
          } />
          <Route path="/manage-departments" element={
            <ProtectedRoute requireSuperuser={true}>
              <ManageDepartments />
            </ProtectedRoute>
          } />
          <Route path="/manage-staff" element={
            <ProtectedRoute requireSuperuser={true}>
              <ManageStaff />
            </ProtectedRoute>
          } />

          <Route path="/change-password" element={
            <ProtectedRoute>
              <ChangePassword />
            </ProtectedRoute>
          } />
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
