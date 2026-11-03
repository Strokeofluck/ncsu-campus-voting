import React from 'react';
import logo from './assets/technician-masthead.webp';
import './technician-preview.css';

export function TechnicianHeader(){
 return <header className="technician-preview-header" aria-label="Technician editor preview">
  <div className="technician-preview-logo"><a href="https://technicianonline.com/" aria-label="Technician — The News Site of NC State University"><img src={logo} alt="Technician" width="396" height="137"/></a></div>
  <nav className="technician-preview-sections" aria-label="Technician sections">
   {['News','Sports','Opinion','Culture','Multimedia'].map(section=><a key={section} href={`https://technicianonline.com/category/${section.toLowerCase()}/`}>{section}</a>)}
   <a href="https://technicianonline.com/submissions/">Submissions</a>
  </nav>
 </header>;
}
