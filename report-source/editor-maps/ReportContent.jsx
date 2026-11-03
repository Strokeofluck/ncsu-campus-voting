import React from 'react';
import {RichNarrative} from '../../data-app-public.jsx';
import {CampusWalkingMap} from './CampusWalkingMap.jsx';
import {CampusPassbyMap} from './CampusPassbyMap.jsx';
import {TechnicianHeader} from './TechnicianHeader.jsx';
import './article.css';
import './editor-maps.css';

export function ReportContent(){
 return <article className="report-content voting-report voting-article voting-editor-maps" aria-label="NC State voting maps — editor preview">
  <TechnicianHeader/>
  <div className="editor-maps-title"><RichNarrative id="editor-maps:title" value="# NC State voting maps"/></div>
  <CampusWalkingMap article editorPreview/>
  <CampusPassbyMap article editorPreview/>
 </article>;
}
