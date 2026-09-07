import React, { useState, useEffect, useContext } from 'react';
import Layout from '../components/Layout';
import { AuthContext } from '../AuthContext';
import StatusBadge from '../components/StatusBadge';
import Timeline from '../components/Timeline';
import api from '../api';
import { Calendar as CalendarIcon, List, GitPullRequest, Search, Filter, X, ChevronLeft, ChevronRight, MapPin, Clock, Users, Building, FileText } from 'lucide-react';

const EventTracker = () => {
  const { user } = useContext(AuthContext);
  const [requests, setRequests] = useState([]);
  const [halls, setHalls] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);

  // Filters & Views
  const [viewMode, setViewMode] = useState('calendar'); // 'calendar' | 'flow' | 'list'
  const [selectedDept, setSelectedDept] = useState('');
  const [selectedStatus, setSelectedStatus] = useState('');
  const [selectedHall, setSelectedHall] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  
  // Calendar Navigation State
  const [currentDate, setCurrentDate] = useState(new Date());
  
  // Selected Event Modal
  const [selectedEvent, setSelectedEvent] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const [reqRes, hallRes, deptRes] = await Promise.all([
          api.get('requests/'),
          api.get('halls/'),
          api.get('departments/').catch(() => ({ data: [] }))
        ]);
        setRequests(reqRes.data);
        setHalls(hallRes.data);
        setDepartments(deptRes.data || []);
      } catch (err) {
        console.error("Failed to load tracker data", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  // Filter requests by search, department, hall, and status
  const filteredRequests = requests.filter(req => {
    if (selectedDept && req.department_name !== selectedDept && req.department !== parseInt(selectedDept)) return false;
    if (selectedHall && req.venue?.toString() !== selectedHall.toString()) return false;
    if (selectedStatus) {
      if (selectedStatus === 'COMPLETED' && (req.status !== 'CONFIRMED' && req.status !== 'APPROVED')) return false;
      if (selectedStatus === 'PENDING' && !req.status.startsWith('PENDING')) return false;
      if (selectedStatus === 'RETURNED' && req.status !== 'RETURNED_FOR_CORRECTION') return false;
    }
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      const nameMatch = req.function_name?.toLowerCase().includes(q);
      const deptMatch = req.department_name?.toLowerCase().includes(q);
      const guestMatch = req.chief_guest_name?.toLowerCase().includes(q);
      const organizerMatch = req.organizer_name?.toLowerCase().includes(q);
      if (!nameMatch && !deptMatch && !guestMatch && !organizerMatch) return false;
    }
    return true;
  });

  // Calendar Date Math
  const year = currentDate.getFullYear();
  const month = currentDate.getMonth();

  const firstDayOfMonth = new Date(year, month, 1);
  const lastDayOfMonth = new Date(year, month + 1, 0);

  const daysInMonth = lastDayOfMonth.getDate();
  const startingDayOfWeek = firstDayOfMonth.getDay(); // 0 = Sun

  const monthNames = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
  ];

  const prevMonth = () => setCurrentDate(new Date(year, month - 1, 1));
  const nextMonth = () => setCurrentDate(new Date(year, month + 1, 1));
  const todayMonth = () => setCurrentDate(new Date());

  // Map events to day numbers for current month
  const getEventsForDay = (dayNum) => {
    const formattedDayStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(dayNum).padStart(2, '0')}`;
    
    return filteredRequests.filter(req => {
      if (!req.start_date) return false;
      const start = req.start_date;
      const end = req.end_date || req.start_date;
      return formattedDayStr >= start && formattedDayStr <= end;
    });
  };

  // Status color helper for calendar items
  const getEventBadgeStyle = (status) => {
    if (status === 'CONFIRMED' || status === 'APPROVED') return { bg: '#dcfce7', text: '#15803d', border: '#bbf7d0' };
    if (status.startsWith('PENDING')) return { bg: '#fef3c7', text: '#b45309', border: '#fde68a' };
    if (status === 'RETURNED_FOR_CORRECTION') return { bg: '#e0e7ff', text: '#4338ca', border: '#c7d2fe' };
    if (status === 'REJECTED' || status === 'CANCELLED') return { bg: '#fee2e2', text: '#b91c1c', border: '#fecaca' };
    return { bg: '#f1f5f9', text: '#475569', border: '#e2e8f0' };
  };

  const getFlowProgress = (status) => {
    const isFullyApproved = status === 'APPROVED' || status === 'CONFIRMED';
    const stages = [
      { key: 'FACULTY', label: 'Faculty Created', done: true },
      { key: 'PENDING_HOD', label: 'HOD Approval', done: isFullyApproved || ['PENDING_DEAN', 'PENDING_MANAGEMENT', 'PENDING_PRINCIPAL', 'PENDING_FINAL_CONFIRMATION'].includes(status) },
      { key: 'PENDING_DEAN', label: 'Dean Computing', done: isFullyApproved || ['PENDING_MANAGEMENT', 'PENDING_PRINCIPAL', 'PENDING_FINAL_CONFIRMATION'].includes(status) },
      { key: 'PENDING_MANAGEMENT', label: 'AO Hall Assign', done: isFullyApproved || ['PENDING_PRINCIPAL', 'PENDING_FINAL_CONFIRMATION'].includes(status) },
      { key: 'PENDING_PRINCIPAL', label: 'Principal Sanction', done: isFullyApproved || ['PENDING_FINAL_CONFIRMATION'].includes(status) },
      { key: 'CONFIRMED', label: 'Final Confirmation', done: isFullyApproved }
    ];
    return stages;
  };

  return (
    <Layout title="Event Tracker & Live Calendar">
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        
        {/* Header Controls */}
        <div className="card" style={{ padding: '1.5rem', marginBottom: '1.5rem', borderRadius: '12px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.5rem' }}>
            <div>
              <h2 style={{ margin: 0, color: 'var(--primary-color)', fontSize: '1.5rem', fontWeight: '700' }}>
                Campus Event Tracker & Flow Dashboard
              </h2>
              <p style={{ margin: '0.25rem 0 0 0', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                Live level-based approval progress, hall time-slot mappings, and event schedule
              </p>
            </div>

            {/* View Mode Toggle */}
            <div style={{ display: 'flex', background: '#f1f5f9', padding: '0.25rem', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
              <button
                onClick={() => setViewMode('calendar')}
                className="btn"
                style={{
                  padding: '0.4rem 0.8rem',
                  fontSize: '0.875rem',
                  background: viewMode === 'calendar' ? 'white' : 'transparent',
                  color: viewMode === 'calendar' ? 'var(--primary-color)' : 'var(--text-secondary)',
                  boxShadow: viewMode === 'calendar' ? '0 1px 3px rgba(0,0,0,0.1)' : 'none',
                  borderRadius: '6px'
                }}
              >
                <CalendarIcon size={16} style={{ marginRight: '0.35rem', verticalAlign: 'middle' }} />
                Interactive Calendar
              </button>
              <button
                onClick={() => setViewMode('flow')}
                className="btn"
                style={{
                  padding: '0.4rem 0.8rem',
                  fontSize: '0.875rem',
                  background: viewMode === 'flow' ? 'white' : 'transparent',
                  color: viewMode === 'flow' ? 'var(--primary-color)' : 'var(--text-secondary)',
                  boxShadow: viewMode === 'flow' ? '0 1px 3px rgba(0,0,0,0.1)' : 'none',
                  borderRadius: '6px'
                }}
              >
                <GitPullRequest size={16} style={{ marginRight: '0.35rem', verticalAlign: 'middle' }} />
                Approval Flow Stepper
              </button>
              <button
                onClick={() => setViewMode('list')}
                className="btn"
                style={{
                  padding: '0.4rem 0.8rem',
                  fontSize: '0.875rem',
                  background: viewMode === 'list' ? 'white' : 'transparent',
                  color: viewMode === 'list' ? 'var(--primary-color)' : 'var(--text-secondary)',
                  boxShadow: viewMode === 'list' ? '0 1px 3px rgba(0,0,0,0.1)' : 'none',
                  borderRadius: '6px'
                }}
              >
                <List size={16} style={{ marginRight: '0.35rem', verticalAlign: 'middle' }} />
                Tabular List
              </button>
            </div>
          </div>

          {/* Filter Bar */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', alignItems: 'center' }}>
            <div style={{ position: 'relative' }}>
              <Search size={16} style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: '#94a3b8' }} />
              <input
                type="text"
                className="form-input"
                placeholder="Search event, organizer, guest..."
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
                style={{ paddingLeft: '2.2rem' }}
              />
            </div>

            <select className="form-input" value={selectedStatus} onChange={e => setSelectedStatus(e.target.value)}>
              <option value="">All Approval Statuses</option>
              <option value="COMPLETED">Confirmed / Approved</option>
              <option value="PENDING">In Active Approval Flow</option>
              <option value="RETURNED">Returned for Correction</option>
            </select>

            <select className="form-input" value={selectedHall} onChange={e => setSelectedHall(e.target.value)}>
              <option value="">All Seminar Halls</option>
              {halls.map(h => <option key={h.id} value={h.id}>{h.hall_name}</option>)}
            </select>

            {user?.role !== 'FACULTY' && (
              <select className="form-input" value={selectedDept} onChange={e => setSelectedDept(e.target.value)}>
                <option value="">All Departments</option>
                {departments.map(d => <option key={d.id} value={d.department_name}>{d.department_name}</option>)}
              </select>
            )}
          </div>
        </div>

        {/* LOADING STATE */}
        {loading ? (
          <div className="card" style={{ padding: '4rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
            <div className="spinner" style={{ margin: '0 auto 1rem auto' }}></div>
            Fetching events and calendar mapping...
          </div>
        ) : (
          <>
            {/* VIEW 1: INTERACTIVE CALENDAR */}
            {viewMode === 'calendar' && (
              <div className="card" style={{ padding: '1.5rem', borderRadius: '12px' }}>
                
                {/* Month Navigator Header */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    <h3 style={{ margin: 0, fontSize: '1.25rem', color: 'var(--primary-color)', fontWeight: 'bold' }}>
                      {monthNames[month]} {year}
                    </h3>
                    <button onClick={todayMonth} className="btn btn-outline" style={{ padding: '0.2rem 0.6rem', fontSize: '0.75rem' }}>
                      Today
                    </button>
                  </div>
                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <button onClick={prevMonth} className="btn btn-outline" style={{ padding: '0.4rem 0.8rem', display: 'flex', alignItems: 'center' }}>
                      <ChevronLeft size={18} /> Prev
                    </button>
                    <button onClick={nextMonth} className="btn btn-outline" style={{ padding: '0.4rem 0.8rem', display: 'flex', alignItems: 'center' }}>
                      Next <ChevronRight size={18} />
                    </button>
                  </div>
                </div>

                {/* Days of Week Header */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: '0.5rem', textAlign: 'center', fontWeight: 'bold', fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
                  <div>Sun</div><div>Mon</div><div>Tue</div><div>Wed</div><div>Thu</div><div>Fri</div><div>Sat</div>
                </div>

                {/* Calendar Grid */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: '0.5rem' }}>
                  {/* Blank slots for previous month */}
                  {Array.from({ length: startingDayOfWeek }).map((_, i) => (
                    <div key={`blank-${i}`} style={{ minHeight: '110px', background: '#f8fafc', borderRadius: '8px', border: '1px border #f1f5f9', opacity: 0.4 }}></div>
                  ))}

                  {/* Days of current month */}
                  {Array.from({ length: daysInMonth }).map((_, i) => {
                    const dayNum = i + 1;
                    const dayEvents = getEventsForDay(dayNum);
                    const isToday = dayNum === new Date().getDate() && month === new Date().getMonth() && year === new Date().getFullYear();

                    return (
                      <div
                        key={`day-${dayNum}`}
                        style={{
                          minHeight: '110px',
                          background: isToday ? '#f0f9ff' : 'white',
                          border: isToday ? '2px solid var(--primary-color)' : '1px solid #e2e8f0',
                          borderRadius: '8px',
                          padding: '0.5rem',
                          display: 'flex',
                          flexDirection: 'column',
                          gap: '0.35rem'
                        }}
                      >
                        <div style={{ fontWeight: 'bold', fontSize: '0.85rem', color: isToday ? 'var(--primary-color)' : '#475569', marginBottom: '0.2rem' }}>
                          {dayNum}
                        </div>

                        {/* Events list inside day cell */}
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem', overflowY: 'auto', maxHeight: '80px' }}>
                          {dayEvents.map(evt => {
                            const badge = getEventBadgeStyle(evt.status);
                            const venueName = halls.find(h => h.id === evt.venue)?.hall_name || 'TBD';
                            return (
                              <div
                                key={evt.id}
                                onClick={() => setSelectedEvent(evt)}
                                style={{
                                  background: badge.bg,
                                  color: badge.text,
                                  border: `1px solid ${badge.border}`,
                                  borderRadius: '4px',
                                  padding: '0.2rem 0.35rem',
                                  fontSize: '0.72rem',
                                  fontWeight: '600',
                                  cursor: 'pointer',
                                  whiteSpace: 'nowrap',
                                  overflow: 'hidden',
                                  textOverflow: 'ellipsis'
                                }}
                                title={`${evt.function_name} (${evt.time_from?.slice(0,5)} - ${evt.time_to?.slice(0,5)}) @ ${venueName}`}
                              >
                                ⏱ {evt.time_from?.slice(0,5)} {evt.function_name}
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* VIEW 2: APPROVAL FLOW STEPPER */}
            {viewMode === 'flow' && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                {filteredRequests.length === 0 ? (
                  <div className="card" style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
                    No events matching selected filters.
                  </div>
                ) : (
                  filteredRequests.map(req => {
                    const flowStages = getFlowProgress(req.status);
                    const venueName = halls.find(h => h.id === req.venue)?.hall_name || 'Unassigned';

                    return (
                      <div key={req.id} className="card" style={{ padding: '1.5rem', borderRadius: '12px', borderLeft: '4px solid var(--primary-color)' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem', marginBottom: '1rem' }}>
                          <div>
                            <span style={{ fontSize: '0.75rem', fontWeight: 'bold', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>
                              #{req.id} • {req.department_name || 'Department'}
                            </span>
                            <h3 style={{ margin: '0.25rem 0', color: 'var(--primary-color)', fontSize: '1.2rem' }}>
                              {req.function_name}
                            </h3>
                            <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', fontSize: '0.85rem', color: '#475569', marginTop: '0.35rem' }}>
                              <span><MapPin size={14} style={{ verticalAlign: 'middle' }} /> {venueName}</span>
                              <span><Clock size={14} style={{ verticalAlign: 'middle' }} /> {req.start_date} ({req.time_from?.slice(0,5)} - {req.time_to?.slice(0,5)})</span>
                              <span><Users size={14} style={{ verticalAlign: 'middle' }} /> {req.number_of_students} Students</span>
                            </div>
                          </div>

                          <div style={{ textAlign: 'right' }}>
                            <StatusBadge status={req.status} />
                            <button
                              onClick={() => setSelectedEvent(req)}
                              className="btn btn-outline"
                              style={{ padding: '0.3rem 0.7rem', fontSize: '0.75rem', marginTop: '0.5rem', display: 'block' }}
                            >
                              View Details & Timeline
                            </button>
                          </div>
                        </div>

                        {/* Approval Stage Stepper Bar */}
                        <div style={{ marginTop: '1.25rem', paddingTop: '1rem', borderTop: '1px solid #f1f5f9' }}>
                          <h4 style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: '0.75rem' }}>
                            Approval Level Hierarchy
                          </h4>
                          <div style={{ display: 'flex', gap: '0.5rem', overflowX: 'auto', paddingBottom: '0.5rem' }}>
                            {flowStages.map((stage, idx) => (
                              <div
                                key={stage.key}
                                style={{
                                  flex: 1,
                                  minWidth: '120px',
                                  background: stage.done ? '#f0fdf4' : '#f8fafc',
                                  border: `1px solid ${stage.done ? '#bbf7d0' : '#e2e8f0'}`,
                                  borderRadius: '6px',
                                  padding: '0.5rem 0.75rem',
                                  fontSize: '0.75rem',
                                  fontWeight: '600',
                                  color: stage.done ? '#166534' : '#64748b'
                                }}
                              >
                                <div style={{ fontSize: '0.68rem', opacity: 0.8 }}>Level {idx + 1}</div>
                                {stage.done ? '✓ ' : '⏳ '}{stage.label}
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    );
                  })
                )}
              </div>
            )}

            {/* VIEW 3: TABULAR LIST */}
            {viewMode === 'list' && (
              <div className="card" style={{ padding: '0', borderRadius: '12px', overflow: 'hidden' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.9rem' }}>
                  <thead>
                    <tr style={{ background: '#f8fafc', borderBottom: '1px solid #e2e8f0', textAlign: 'left', color: 'var(--text-secondary)' }}>
                      <th style={{ padding: '1rem' }}>ID & Event</th>
                      <th style={{ padding: '1rem' }}>Department</th>
                      <th style={{ padding: '1rem' }}>Date & Timing</th>
                      <th style={{ padding: '1rem' }}>Venue</th>
                      <th style={{ padding: '1rem' }}>Status</th>
                      <th style={{ padding: '1rem' }}>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredRequests.length === 0 ? (
                      <tr>
                        <td colSpan="6" style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
                          No events found matching criteria.
                        </td>
                      </tr>
                    ) : (
                      filteredRequests.map(req => (
                        <tr key={req.id} style={{ borderBottom: '1px solid #f1f5f9' }}>
                          <td style={{ padding: '1rem' }}>
                            <div style={{ fontWeight: 'bold', color: 'var(--primary-color)' }}>{req.function_name}</div>
                            <div style={{ fontSize: '0.75rem', color: '#64748b' }}>#{req.id} • {req.organizer_name}</div>
                          </td>
                          <td style={{ padding: '1rem' }}>{req.department_name || 'N/A'}</td>
                          <td style={{ padding: '1rem' }}>
                            <div>{req.start_date}</div>
                            <div style={{ fontSize: '0.75rem', color: '#64748b' }}>{req.time_from?.slice(0,5)} - {req.time_to?.slice(0,5)}</div>
                          </td>
                          <td style={{ padding: '1rem' }}>{halls.find(h => h.id === req.venue)?.hall_name || 'TBD'}</td>
                          <td style={{ padding: '1rem' }}><StatusBadge status={req.status} /></td>
                          <td style={{ padding: '1rem' }}>
                            <button onClick={() => setSelectedEvent(req)} className="btn btn-outline" style={{ padding: '0.3rem 0.6rem', fontSize: '0.75rem' }}>
                              Details
                            </button>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            )}
          </>
        )}

        {/* QUICK EVENT PREVIEW MODAL */}
        {selectedEvent && (
          <div style={{
            position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
            background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center',
            zIndex: 1000, padding: '1rem'
          }}>
            <div className="card" style={{ maxWidth: '650px', width: '100%', maxHeight: '90vh', overflowY: 'auto', padding: '1.75rem', borderRadius: '14px', position: 'relative' }}>
              <button
                onClick={() => setSelectedEvent(null)}
                style={{ position: 'absolute', top: '1.25rem', right: '1.25rem', background: 'none', border: 'none', cursor: 'pointer', color: '#64748b' }}
              >
                <X size={20} />
              </button>

              <div style={{ marginBottom: '1.25rem', paddingRight: '2rem' }}>
                <span style={{ fontSize: '0.75rem', fontWeight: 'bold', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>
                  Request #{selectedEvent.id} • {selectedEvent.department_name}
                </span>
                <h2 style={{ margin: '0.25rem 0 0.5rem 0', color: 'var(--primary-color)' }}>
                  {selectedEvent.function_name}
                </h2>
                <StatusBadge status={selectedEvent.status} />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', background: '#f8fafc', padding: '1rem', borderRadius: '8px', border: '1px solid #e2e8f0', marginBottom: '1.5rem', fontSize: '0.875rem' }}>
                <div><strong>Date:</strong> {selectedEvent.start_date} to {selectedEvent.end_date || selectedEvent.start_date}</div>
                <div><strong>Timing:</strong> {selectedEvent.time_from} - {selectedEvent.time_to}</div>
                <div><strong>Venue:</strong> {halls.find(h => h.id === selectedEvent.venue)?.hall_name || 'None Assigned'}</div>
                <div><strong>Audience:</strong> {selectedEvent.number_of_students} ({selectedEvent.class_name || 'N/A'})</div>
                <div><strong>Organizer:</strong> {selectedEvent.organizer_name} ({selectedEvent.organizer_contact})</div>
                <div><strong>Chief Guest:</strong> {selectedEvent.chief_guest_name || 'N/A'}</div>
              </div>

              {/* Approval Timeline Component */}
              <h4 style={{ margin: '0 0 0.75rem 0', color: 'var(--primary-color)' }}>Approval Log & History</h4>
              <Timeline logs={selectedEvent.approval_logs || []} currentStatus={selectedEvent.status} />

              <div style={{ marginTop: '1.5rem', textAlign: 'right' }}>
                <button onClick={() => setSelectedEvent(null)} className="btn btn-outline" style={{ padding: '0.4rem 1rem' }}>
                  Close
                </button>
              </div>
            </div>
          </div>
        )}

      </div>
    </Layout>
  );
};

export default EventTracker;
