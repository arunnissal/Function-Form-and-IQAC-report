import React, { useState, useEffect, useContext } from 'react';
import api from '../api';
import Layout from '../components/Layout';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../AuthContext';
import { Calendar, momentLocalizer } from 'react-big-calendar';
import moment from 'moment';
import 'react-big-calendar/lib/css/react-big-calendar.css';

const localizer = momentLocalizer(moment);

export default function EventCalendar() {
  const { user } = useContext(AuthContext);
  const navigate = useNavigate();
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentView, setCurrentView] = useState('month');
  const [currentDate, setCurrentDate] = useState(new Date());

  useEffect(() => {
    fetchApprovedRequests();
  }, []);

  const fetchApprovedRequests = async () => {
    try {
      const response = await api.get('requests/?all_approved=true');
      setRequests(response.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleForceCancel = async (id) => {
    if (window.confirm("EMERGENCY: Are you sure you want to forcefully cancel this approved event? This cannot be undone.")) {
      try {
        await api.post(`requests/${id}/cancel_request/`);
        fetchApprovedRequests();
      } catch (err) {
        console.error(err);
        alert("Failed to cancel event.");
      }
    }
  };

  const events = requests.map(req => {
    // Robust date parsing
    const startDateStr = req.start_date || new Date().toISOString().split('T')[0];
    const timeFrom = req.time_from || '08:00:00';
    let startDate = new Date(`${startDateStr}T${timeFrom}`);
    
    let endDate;
    if (req.end_date && req.time_to) {
      endDate = new Date(`${req.end_date}T${req.time_to}`);
    } else if (req.time_to) {
      endDate = new Date(`${startDateStr}T${req.time_to}`);
    } else {
      endDate = new Date(`${req.end_date || startDateStr}T18:00:00`);
    }

    // Fallback if Date is Invalid
    if (isNaN(startDate.getTime())) {
      startDate = new Date(startDateStr);
    }
    if (isNaN(endDate.getTime())) {
      endDate = new Date(startDateStr);
    }

    return {
      id: req.id,
      title: `${req.function_name} - ${req.department_code || 'General'}`,
      start: startDate,
      end: endDate,
      resource: req
    };
  });

  const eventStyleGetter = (event, start, end, isSelected) => {
    const backgroundColor = 'var(--primary-color)';
    const style = {
      backgroundColor,
      borderRadius: '4px',
      opacity: 0.9,
      color: 'white',
      border: '0px',
      display: 'block'
    };
    return { style };
  };

  return (
    <Layout title="Event Calendar">
      <div style={{ maxWidth: '1200px', margin: '0 auto'}}>
        <div style={{ background: 'white', borderRadius: '8px', boxShadow: 'var(--shadow-md)', overflow: 'hidden', padding: '2rem'}}>
          {loading ? (
            <div style={{padding: '2rem', textAlign: 'center', color: 'var(--text-secondary)'}}>Loading events...</div>
          ) : (
            <div style={{ height: '700px' }}>
              <Calendar
                localizer={localizer}
                events={events}
                startAccessor="start"
                endAccessor="end"
                style={{ height: '100%' }}
                views={['month', 'week', 'day']}
                view={currentView}
                onView={(view) => setCurrentView(view)}
                date={currentDate}
                onNavigate={(date) => setCurrentDate(date)}
                eventPropGetter={eventStyleGetter}
                tooltipAccessor={(event) => `${event.title}\nVenue: ${event.resource.venue_name || 'TBD'}\nTime: ${event.resource.time_from} - ${event.resource.time_to}`}
                onSelectEvent={(event) => {
                  navigate(`/request/${event.resource.id}`);
                }}
              />
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}
