import React, { useState, useEffect } from 'react';
import api from '../api';
import { useNavigate, useParams } from 'react-router-dom';
import Layout from '../components/Layout';

export default function EditRequest() {
  const navigate = useNavigate();
  const { id } = useParams();
  const [step, setStep] = useState(1);
  const [halls, setHalls] = useState([]);
  const [submitError, setSubmitError] = useState('');
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  
  // Step 1: Basic Function Details
  const [basic, setBasic] = useState({
    function_name: '', function_type: '', start_date: '', end_date: '',
    number_of_days: 1, time_from: '', time_to: '', venue: '', type_of_training: '',
    number_of_students: 0, class_name: '', organizer_name: '', organizer_contact: '',
    chief_guest_name: '', chief_guest_designation: '', chief_guest_organization: ''
  });

  // Step 2: Guest House
  const [guest, setGuest] = useState({
    required: false, number_of_persons: 0, from_date: '', to_date: ''
  });

  // Step 3: Refreshment
  const [refreshment, setRefreshment] = useState({
    tea_required: false, coffee_required: false, snacks_required: false,
    required_time: '', payment_through: 'ASSOCIATION', tiffin_count: 0,
    normal_lunch_count: 0, veg_lunch_count: 0, non_veg_lunch_count: 0
  });

  // Step 4: Power/System
  const [power, setPower] = useState({
    mic_required: false, mic_type: 'Cordless', number_of_mics: 0,
    ac_required: false, projector_required: false, laptop_required: false,
    photographer_required: false, photographer_type: 'LAB_TECHNICIAN'
  });

  // Step 5: Memento
  const [memento, setMemento] = useState({
    required: false, honorarium_worth: '', quantity: 0, dias_seats: 0,
    audience_seats: 0, table_cloths: 0, reception_items: ''
  });

  // Step 6: Transport
  const [transport, setTransport] = useState({
    required: false, date: '', pickup_location: '', pickup_time: '',
    drop_date: '', drop_time: '', drop_location: '', pickup_person_name: '', pickup_person_contact: ''
  });

  useEffect(() => {
    const fetchHalls = async () => {
      try {
        const response = await api.get('halls/');
        setHalls(response.data);
      } catch (err) {
        console.error(err);
      }
    };
    fetchHalls();

    if (id) {
      const fetchRequest = async () => {
        try {
          const res = await api.get(`requests/${id}/`);
          const data = res.data;
          
          setBasic({
            function_name: data.function_name || '', function_type: data.function_type || '', start_date: data.start_date || '', end_date: data.end_date || '',
            number_of_days: data.number_of_days || 1, time_from: data.time_from || '', time_to: data.time_to || '', venue: data.venue || '', type_of_training: data.type_of_training || '',
            number_of_students: data.number_of_students || 0, class_name: data.class_name || '', organizer_name: data.organizer_name || '', organizer_contact: data.organizer_contact || '',
            chief_guest_name: data.chief_guest_name || '', chief_guest_designation: data.chief_guest_designation || '', chief_guest_organization: data.chief_guest_organization || ''
          });

          if (data.guest_house) setGuest(data.guest_house);
          if (data.refreshment) setRefreshment(data.refreshment);
          if (data.power_camera) setPower(data.power_camera);
          if (data.memento) setMemento(data.memento);
          if (data.transport) setTransport(data.transport);
          
        } catch (err) {
          console.error("Failed to fetch request", err);
        }
      };
      fetchRequest();
    }
  }, [id]);

  const handleNext = (e) => {
    e.preventDefault();
    if (step === 1 && basic.venue) {
      const selectedHall = halls.find(h => h.id.toString() === basic.venue.toString());
      if (selectedHall && parseInt(basic.number_of_students) > selectedHall.capacity) {
        setSubmitError(`Number of students (${basic.number_of_students}) exceeds the maximum capacity of ${selectedHall.hall_name} (${selectedHall.capacity} seats).`);
        return;
      }
    }
    setSubmitError('');
    setStep(prev => prev + 1);
  };

  const handlePrev = () => {
    setStep(prev => prev - 1);
  };

  const triggerConfirmation = (e) => {
    e.preventDefault();
    setShowConfirmModal(true);
  };

  const handleSubmit = async (e) => {
    if (e) e.preventDefault();
    setSubmitError('');
    try {
      const sanitizePayload = (obj) => {
        const sanitized = {};
        const charFields = [
          'function_name', 'function_type', 'type_of_training', 'class_name',
          'organizer_name', 'organizer_contact', 'chief_guest_name', 'chief_guest_designation', 'chief_guest_organization',
          'pickup_location', 'drop_location', 'pickup_person_name', 'pickup_person_contact',
          'honorarium_worth', 'reception_items', 'mic_type', 'photographer_type', 'payment_through', 'room_type'
        ];

        for (const key in obj) {
          if (obj[key] === "") {
            sanitized[key] = charFields.includes(key) ? "" : null;
          }
          else if (typeof obj[key] === 'object' && obj[key] !== null && !Array.isArray(obj[key])) {
            sanitized[key] = sanitizePayload(obj[key]);
          }
          else {
            sanitized[key] = obj[key];
          }
        }
        return sanitized;
      };

      const payload = sanitizePayload({
        ...basic,
        guest_house: guest,
        refreshment: refreshment,
        power_camera: power,
        memento: memento,
        transport: transport
      });

      await api.put(`requests/${id}/`, payload);
      navigate('/approvals');
    } catch (err) {
      console.error(err);
      if (err.response && err.response.data) {
        setSubmitError(JSON.stringify(err.response.data));
      } else {
        setSubmitError("Failed to submit request.");
      }
    }
  };

  const renderStepIcon = (num, title, icon) => (
    <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center', opacity: step >= num ? 1 : 0.5}}>
      <div style={{
        width: '32px', height: '32px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center',
        background: step === num ? 'var(--primary-color)' : (step > num ? '#10b981' : '#e2e8f0'),
        color: step >= num ? 'white' : 'var(--text-secondary)', fontWeight: 'bold', marginBottom: '0.5rem'
      }}>
        {step > num ? '✓' : num}
      </div>
    </div>
  );

  return (
    <Layout title={`Edit Request #${id}`}>
      <div style={{ maxWidth: '900px', margin: '0 auto', background: 'white', padding: '2rem', borderRadius: '8px', boxShadow: 'var(--shadow-md)'}}>
        
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '2rem', position: 'relative' }}>
          <div style={{position: 'absolute', top: '16px', left: '0', right: '0', height: '2px', background: '#e2e8f0', zIndex: 0}}></div>
          <div style={{zIndex: 1, width: '100%', display: 'flex', justifyContent: 'space-between'}}>
            {renderStepIcon(1)}
            {renderStepIcon(2)}
            {renderStepIcon(3)}
            {renderStepIcon(4)}
            {renderStepIcon(5)}
            {renderStepIcon(6)}
            {renderStepIcon(7)}
          </div>
        </div>

        {submitError && (
          <div style={{padding: '1rem', background: '#fee2e2', color: '#b91c1c', borderRadius: '4px', marginBottom: '1.5rem'}}>
            <strong>Error:</strong> {submitError}
          </div>
        )}

        <form onSubmit={step === 7 ? triggerConfirmation : handleNext}>
          
          {step === 1 && (
            <div>
              <h3 style={{color: 'var(--primary-color)', marginBottom: '1.5rem'}}>1. Basic Function Details</h3>
              <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem'}}>
                <div>
                  <label className="form-label">Name of the Function *</label>
                  <input type="text" className="form-input" required value={basic.function_name} onChange={e => setBasic({...basic, function_name: e.target.value})} />
                </div>
                <div>
                  <label className="form-label">Type of Function *</label>
                  <input type="text" className="form-input" required value={basic.function_type} onChange={e => setBasic({...basic, function_type: e.target.value})} />
                </div>
                <div>
                  <label className="form-label">Start Date *</label>
                  <input type="date" className="form-input" required value={basic.start_date} onChange={e => setBasic({...basic, start_date: e.target.value})} />
                </div>
                <div>
                  <label className="form-label">End Date</label>
                  <input type="date" className="form-input" value={basic.end_date} onChange={e => setBasic({...basic, end_date: e.target.value})} />
                </div>
                <div>
                  <label className="form-label">Time From *</label>
                  <input type="time" className="form-input" required value={basic.time_from} onChange={e => setBasic({...basic, time_from: e.target.value})} />
                </div>
                <div>
                  <label className="form-label">Time To *</label>
                  <input type="time" className="form-input" required value={basic.time_to} onChange={e => setBasic({...basic, time_to: e.target.value})} />
                </div>
                <div>
                  <label className="form-label">No. of Days *</label>
                  <input type="number" className="form-input" required min="1" value={basic.number_of_days} onChange={e => setBasic({...basic, number_of_days: e.target.value})} />
                </div>
                <div>
                  <label className="form-label">Venue *</label>
                  <select className="form-input" required value={basic.venue} onChange={e => setBasic({...basic, venue: e.target.value})}>
                    <option value="">Select Venue...</option>
                    {halls.map(h => <option key={h.id} value={h.id}>{h.hall_name} (Capacity: {h.capacity})</option>)}
                  </select>
                </div>
                <div>
                  <label className="form-label">No. of Students / Class</label>
                  <div style={{display: 'flex', gap: '0.5rem'}}>
                    <input type="number" className="form-input" placeholder="Count" value={basic.number_of_students} onChange={e => setBasic({...basic, number_of_students: e.target.value})} />
                    <input type="text" className="form-input" placeholder="Class Name" value={basic.class_name} onChange={e => setBasic({...basic, class_name: e.target.value})} />
                  </div>
                </div>
                <div>
                  <label className="form-label">Type of Training</label>
                  <input type="text" className="form-input" value={basic.type_of_training} onChange={e => setBasic({...basic, type_of_training: e.target.value})} />
                </div>
              </div>

              <h4 style={{marginTop: '2rem', marginBottom: '1rem'}}>Organizer & Guest Details</h4>
              <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem'}}>
                <div>
                  <label className="form-label">Organizer Name *</label>
                  <input type="text" className="form-input" required value={basic.organizer_name} onChange={e => setBasic({...basic, organizer_name: e.target.value})} />
                </div>
                <div>
                  <label className="form-label">Organizer Contact Number *</label>
                  <input type="text" className="form-input" required value={basic.organizer_contact} onChange={e => setBasic({...basic, organizer_contact: e.target.value})} />
                </div>
                <div>
                  <label className="form-label">Chief Guest Name</label>
                  <input type="text" className="form-input" value={basic.chief_guest_name} onChange={e => setBasic({...basic, chief_guest_name: e.target.value})} />
                </div>
                <div>
                  <label className="form-label">Designation</label>
                  <input type="text" className="form-input" value={basic.chief_guest_designation} onChange={e => setBasic({...basic, chief_guest_designation: e.target.value})} />
                </div>
                <div style={{gridColumn: '1 / -1'}}>
                  <label className="form-label">College / Industry</label>
                  <input type="text" className="form-input" value={basic.chief_guest_organization} onChange={e => setBasic({...basic, chief_guest_organization: e.target.value})} />
                </div>
              </div>
            </div>
          )}

          {step === 2 && (
            <div>
              <h3 style={{color: 'var(--primary-color)', marginBottom: '1.5rem'}}>2. Guest House Requirement</h3>
              <div style={{marginBottom: '1.5rem'}}>
                <label style={{display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 'bold'}}>
                  <input type="checkbox" checked={guest.required} onChange={e => setGuest({...guest, required: e.target.checked})} />
                  Guest House Required?
                </label>
              </div>
              {guest.required && (
                <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', padding: '1rem', background: '#f8fafc', borderRadius: '8px'}}>
                  <div style={{gridColumn: '1 / -1'}}>
                    <label className="form-label">Number of Persons</label>
                    <input type="number" className="form-input" value={guest.number_of_persons} onChange={e => setGuest({...guest, number_of_persons: e.target.value})} />
                  </div>
                  <div>
                    <label className="form-label">From Date</label>
                    <input type="date" className="form-input" value={guest.from_date} onChange={e => setGuest({...guest, from_date: e.target.value})} />
                  </div>
                  <div>
                    <label className="form-label">To Date</label>
                    <input type="date" className="form-input" value={guest.to_date} onChange={e => setGuest({...guest, to_date: e.target.value})} />
                  </div>
                </div>
              )}
            </div>
          )}

          {step === 3 && (
            <div>
              <h3 style={{color: 'var(--primary-color)', marginBottom: '1.5rem'}}>3. Refreshment / Lunch Requirement</h3>
              <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem'}}>
                <div>
                  <label className="form-label">Refreshment Items</label>
                  <div style={{display: 'flex', flexDirection: 'column', gap: '0.5rem'}}>
                    <label><input type="checkbox" checked={refreshment.tea_required} onChange={e => setRefreshment({...refreshment, tea_required: e.target.checked})} /> Tea</label>
                    <label><input type="checkbox" checked={refreshment.coffee_required} onChange={e => setRefreshment({...refreshment, coffee_required: e.target.checked})} /> Coffee</label>
                    <label><input type="checkbox" checked={refreshment.snacks_required} onChange={e => setRefreshment({...refreshment, snacks_required: e.target.checked})} /> Snacks</label>
                  </div>
                </div>
                <div>
                  <label className="form-label">Required Time</label>
                  <input type="time" className="form-input" value={refreshment.required_time} onChange={e => setRefreshment({...refreshment, required_time: e.target.value})} />
                  <label className="form-label" style={{marginTop: '1rem'}}>Payment Through</label>
                  <select className="form-input" value={refreshment.payment_through} onChange={e => setRefreshment({...refreshment, payment_through: e.target.value})}>
                    <option value="ASSOCIATION">Association Account</option>
                    <option value="INSTITUTION">Institution Account</option>
                  </select>
                </div>
              </div>
              <h4 style={{marginTop: '2rem', marginBottom: '1rem'}}>Exact Numbers</h4>
              <div style={{display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem'}}>
                <div>
                  <label className="form-label">Tiffin</label>
                  <input type="number" className="form-input" value={refreshment.tiffin_count} onChange={e => setRefreshment({...refreshment, tiffin_count: e.target.value})} />
                </div>
                <div>
                  <label className="form-label">Normal Lunch</label>
                  <input type="number" className="form-input" value={refreshment.normal_lunch_count} onChange={e => setRefreshment({...refreshment, normal_lunch_count: e.target.value})} />
                </div>
                <div>
                  <label className="form-label">Special Lunch (Veg)</label>
                  <input type="number" className="form-input" value={refreshment.veg_lunch_count} onChange={e => setRefreshment({...refreshment, veg_lunch_count: e.target.value})} />
                </div>
                <div>
                  <label className="form-label">Special (Non-Veg)</label>
                  <input type="number" className="form-input" value={refreshment.non_veg_lunch_count} onChange={e => setRefreshment({...refreshment, non_veg_lunch_count: e.target.value})} />
                </div>
              </div>
            </div>
          )}

          {step === 4 && (
            <div>
              <h3 style={{color: 'var(--primary-color)', marginBottom: '1.5rem'}}>4. Power / System / Camera Requirement</h3>
              <div style={{display: 'flex', flexDirection: 'column', gap: '1.5rem'}}>
                <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', alignItems: 'center'}}>
                  <label style={{fontWeight: 'bold'}}><input type="checkbox" checked={power.mic_required} onChange={e => setPower({...power, mic_required: e.target.checked})} /> Mic Arrangement Required?</label>
                  {power.mic_required && (
                    <div style={{display: 'flex', gap: '0.5rem'}}>
                      <input type="text" className="form-input" placeholder="Type" value={power.mic_type} onChange={e => setPower({...power, mic_type: e.target.value})} />
                      <input type="number" className="form-input" style={{width: '80px'}} value={power.number_of_mics} onChange={e => setPower({...power, number_of_mics: e.target.value})} />
                    </div>
                  )}
                </div>
                <div style={{display: 'flex', gap: '2rem'}}>
                  <label style={{fontWeight: 'bold'}}><input type="checkbox" checked={power.ac_required} onChange={e => setPower({...power, ac_required: e.target.checked})} /> A/C Arrangement</label>
                  <label style={{fontWeight: 'bold'}}><input type="checkbox" checked={power.projector_required} onChange={e => setPower({...power, projector_required: e.target.checked})} /> LCD Projector</label>
                  <label style={{fontWeight: 'bold'}}><input type="checkbox" checked={power.laptop_required} onChange={e => setPower({...power, laptop_required: e.target.checked})} /> Laptop</label>
                </div>
                <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', alignItems: 'center'}}>
                  <label style={{fontWeight: 'bold'}}><input type="checkbox" checked={power.photographer_required} onChange={e => setPower({...power, photographer_required: e.target.checked})} /> Photograph Facility Required?</label>
                  {power.photographer_required && (
                    <div>
                      <select className="form-input" value={power.photographer_type} onChange={e => setPower({...power, photographer_type: e.target.value})}>
                        <option value="LAB_TECHNICIAN">Lab Technician</option>
                        <option value="OFFICIAL">Official Photographer</option>
                      </select>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {step === 5 && (
            <div>
              <h3 style={{color: 'var(--primary-color)', marginBottom: '1.5rem'}}>5. Memento / Seating / Reception</h3>
              <div style={{marginBottom: '1.5rem'}}>
                <label style={{fontWeight: 'bold'}}><input type="checkbox" checked={memento.required} onChange={e => setMemento({...memento, required: e.target.checked})} /> Memento / Honorarium for Chief Guest?</label>
              </div>
              {memento.required && (
                <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '2rem'}}>
                  <div>
                    <label className="form-label">Worth of (Rs)</label>
                    <input type="text" className="form-input" value={memento.honorarium_worth} onChange={e => setMemento({...memento, honorarium_worth: e.target.value})} />
                  </div>
                  <div>
                    <label className="form-label">Quantity</label>
                    <input type="number" className="form-input" value={memento.quantity} onChange={e => setMemento({...memento, quantity: e.target.value})} />
                  </div>
                </div>
              )}
              
              <h4 style={{marginBottom: '1rem'}}>No. of Seating Arrangements</h4>
              <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem', marginBottom: '1.5rem'}}>
                <div>
                  <label className="form-label">a) Dias</label>
                  <input type="number" className="form-input" value={memento.dias_seats} onChange={e => setMemento({...memento, dias_seats: e.target.value})} />
                </div>
                <div>
                  <label className="form-label">b) Audience</label>
                  <input type="number" className="form-input" value={memento.audience_seats} onChange={e => setMemento({...memento, audience_seats: e.target.value})} />
                </div>
                <div>
                  <label className="form-label">No. of Table Cloths</label>
                  <input type="number" className="form-input" value={memento.table_cloths} onChange={e => setMemento({...memento, table_cloths: e.target.value})} />
                </div>
              </div>
              <div>
                <label className="form-label">Reception Item Requirements</label>
                <textarea 
                  className="form-input" 
                  rows="3" 
                  value={memento.reception_items} 
                  onChange={e => setMemento({...memento, reception_items: e.target.value})}
                  placeholder="e.g., Flower Bouquet (3), Shawls (3), Welcome Kit (3), Name Plates (8), Drinking Water Bottles (300), Podium Decoration, Stage Floral Decoration"
                ></textarea>
              </div>
            </div>
          )}

          {step === 6 && (
            <div>
              <h3 style={{color: 'var(--primary-color)', marginBottom: '1.5rem'}}>6. Transport Requirement</h3>
              <div style={{marginBottom: '1.5rem'}}>
                <label style={{fontWeight: 'bold'}}><input type="checkbox" checked={transport.required} onChange={e => setTransport({...transport, required: e.target.checked})} /> Transport Required?</label>
              </div>
              {transport.required && (
                <div>
                  <h4 style={{marginBottom: '1rem', color: 'var(--text-secondary)'}}>Pickup Details</h4>
                  <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem', marginBottom: '2rem'}}>
                    <div>
                      <label className="form-label">Date</label>
                      <input type="date" className="form-input" value={transport.date} onChange={e => setTransport({...transport, date: e.target.value})} />
                    </div>
                    <div>
                      <label className="form-label">Time</label>
                      <input type="time" className="form-input" value={transport.pickup_time} onChange={e => setTransport({...transport, pickup_time: e.target.value})} />
                    </div>
                    <div>
                      <label className="form-label">Location</label>
                      <input type="text" className="form-input" value={transport.pickup_location} onChange={e => setTransport({...transport, pickup_location: e.target.value})} />
                    </div>
                  </div>

                  <h4 style={{marginBottom: '1rem', color: 'var(--text-secondary)'}}>Drop Details</h4>
                  <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem', marginBottom: '2rem'}}>
                    <div>
                      <label className="form-label">Date</label>
                      <input type="date" className="form-input" value={transport.drop_date} onChange={e => setTransport({...transport, drop_date: e.target.value})} />
                    </div>
                    <div>
                      <label className="form-label">Time</label>
                      <input type="time" className="form-input" value={transport.drop_time} onChange={e => setTransport({...transport, drop_time: e.target.value})} />
                    </div>
                    <div>
                      <label className="form-label">Location</label>
                      <input type="text" className="form-input" value={transport.drop_location} onChange={e => setTransport({...transport, drop_location: e.target.value})} />
                    </div>
                  </div>

                  <h4 style={{marginBottom: '1rem', color: 'var(--text-secondary)'}}>Contact Person</h4>
                  <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem'}}>
                    <div>
                      <label className="form-label">Name</label>
                      <input type="text" className="form-input" value={transport.pickup_person_name} onChange={e => setTransport({...transport, pickup_person_name: e.target.value})} />
                    </div>
                    <div>
                      <label className="form-label">Contact Number</label>
                      <input type="text" className="form-input" value={transport.pickup_person_contact} onChange={e => setTransport({...transport, pickup_person_contact: e.target.value})} />
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {step === 7 && (
            <div style={{textAlign: 'center', padding: '2rem'}}>
              <div style={{fontSize: '4rem', marginBottom: '1rem'}}>📝</div>
              <h2>Ready to Update?</h2>
              <p style={{color: 'var(--text-secondary)', marginBottom: '2rem'}}>
                You have updated the sections. Click the button below to review your details and save the updated requirements.
              </p>
              
              <div style={{background: '#f8fafc', border: '1px solid #e2e8f0', padding: '1.5rem', borderRadius: '8px', textAlign: 'left', marginBottom: '2rem'}}>
                <h4 style={{margin: '0 0 1rem 0', color: 'var(--primary-color)', borderBottom: '2px solid var(--border-color)', paddingBottom: '0.5rem'}}>Full Request Summary</h4>
                
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                  <div>
                    <h5 style={{ color: 'var(--text-secondary)' }}>Basic Details</h5>
                    <ul style={{ listStyleType: 'none', padding: 0, margin: 0, fontSize: '0.875rem' }}>
                      <li><strong>Function:</strong> {basic.function_name} ({basic.function_type})</li>
                      <li><strong>Dates:</strong> {basic.start_date} to {basic.end_date} ({basic.number_of_days} days)</li>
                      <li><strong>Timing:</strong> {basic.time_from} - {basic.time_to}</li>
                      <li><strong>Venue:</strong> {halls.find(h => h.id.toString() === basic.venue?.toString())?.hall_name || 'None'}</li>
                      <li><strong>Students / Class:</strong> {basic.number_of_students} / {basic.class_name || 'N/A'}</li>
                      <li><strong>Organizer:</strong> {basic.organizer_name} ({basic.organizer_contact})</li>
                      <li><strong>Chief Guest:</strong> {basic.chief_guest_name} - {basic.chief_guest_designation}</li>
                    </ul>
                  </div>

                  <div>
                    <h5 style={{ color: 'var(--text-secondary)' }}>Resource Requirements</h5>
                    <ul style={{ listStyleType: 'none', padding: 0, margin: 0, fontSize: '0.875rem' }}>
                      {guest.required && <li><strong>Guest House:</strong> {guest.room_type} Room</li>}
                      {(refreshment.tea_required || refreshment.coffee_required) && <li><strong>Refreshments:</strong> VIP: {refreshment.vip_count}, Staff: {refreshment.staff_count}, Students: {refreshment.student_count}</li>}
                      {power.mic_required && <li><strong>Power/Audio:</strong> Mics (Cordless: {power.cordless_mics}, Collar: {power.collar_mics}), A/C: {power.ac_required ? 'Yes' : 'No'}</li>}
                      {memento.required && <li><strong>Memento:</strong> {memento.quantity}x (Rs. {memento.honorarium_worth})</li>}
                      {transport.required && <li><strong>Transport:</strong> Pickup: {transport.pickup_location} @ {transport.pickup_time}</li>}
                    </ul>
                  </div>
                </div>

                {(memento.reception_items) && (
                  <div style={{marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid var(--border-color)'}}>
                    <h5 style={{ color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>Reception & Other Details</h5>
                    <p style={{fontSize: '0.875rem', margin: 0}}><strong>Reception Items:</strong> {memento.reception_items}</p>
                    <p style={{fontSize: '0.875rem', margin: 0}}><strong>Seating:</strong> Dias ({memento.dias_seats}), Audience ({memento.audience_seats}), Table Cloths ({memento.table_cloths})</p>
                  </div>
                )}
              </div>

            </div>
          )}

          <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '2rem', paddingTop: '2rem', borderTop: '1px solid var(--border-color)' }}>
            <button type="button" onClick={handlePrev} className="btn btn-outline" disabled={step === 1}>
              &larr; Previous
            </button>
            
            {step < 7 ? (
              <button type="submit" className="btn btn-primary">
                Next Step &rarr;
              </button>
            ) : (
              <button type="button" onClick={triggerConfirmation} className="btn" style={{background: '#10b981', color: 'white'}}>
                Save Updated Request
              </button>
            )}
          </div>
        </form>
      </div>

      {showConfirmModal && (
        <div style={{position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000}}>
          <div style={{background: 'white', padding: '2rem', borderRadius: '8px', width: '500px', maxWidth: '90%', textAlign: 'left'}}>
            <h3 style={{color: 'var(--primary-color)', marginBottom: '1rem'}}>Confirm Updates</h3>
            <div style={{background: '#fef3c7', color: '#92400e', padding: '1rem', borderRadius: '6px', marginBottom: '1.5rem', fontSize: '0.875rem', lineHeight: '1.5'}}>
              <strong>Regulations & Final Warning:</strong>
              <ul style={{margin: '0.5rem 0 0 1.5rem', padding: 0}}>
                <li>I declare that the updated details provided above are true and accurate.</li>
                <li>Any additional resources requested here are subject to further approval.</li>
              </ul>
            </div>
            <p style={{marginBottom: '2rem'}}>Are you absolutely sure you want to save these changes?</p>
            <div style={{display: 'flex', justifyContent: 'flex-end', gap: '1rem'}}>
              <button onClick={() => setShowConfirmModal(false)} className="btn btn-outline">Go Back</button>
              <button onClick={handleSubmit} className="btn" style={{background: '#10b981', color: 'white'}}>I Agree, Save Updates</button>
            </div>
          </div>
        </div>
      )}
    </Layout>
  );
}
