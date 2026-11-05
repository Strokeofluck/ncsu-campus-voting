import React from 'react';
import {RichNarrative,useDataApp} from '../../data-app-public.jsx';
import {CampusWalkingMap} from './CampusWalkingMap.jsx';
import {CampusPassbyMap} from './CampusPassbyMap.jsx';
import {AgeGrowthChart} from './AgeGrowthChart.jsx';
import {YoungestBenchmark} from './YoungestBenchmark.jsx';
import {FullElectionContext} from './FullElectionContext.jsx';
import './article.css';
import './editor-maps.css';

export function ReportContent(){
 const {snapshot}=useDataApp(),youngest=snapshot.queries.age_growth_benchmarks.rows.find(row=>row.cohort==='18–24');
 return <article className="report-content voting-report voting-article voting-editor-maps" aria-label="NC State voting visuals — editor preview">
  <div className="editor-maps-title"><RichNarrative id="editor-maps:title" value="# NC State voting visuals"/></div>
  <AgeGrowthChart/>
  <YoungestBenchmark row={youngest}/>
  <FullElectionContext/>
  <CampusWalkingMap article editorPreview/>
  <CampusPassbyMap article editorPreview/>
 </article>;
}
