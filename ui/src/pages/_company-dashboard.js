import React from "react";
import { Col, Row, Button } from "antd";

const style = { background: "white", padding: "5px 0" };

const CompanyDashboard = ({ company }) => {
  return (
    <div className="company-dashboard">
      <h2 style={{ display: "inline-block", verticalAlign: "middle" }}>
        {company?.business_brief?.company_name}
      </h2>{" "}
      &nbsp;
      <div style={{ display: "inline-block", textAlign: "right" }}>
        {company?.business_brief?.company_name && (
          <Button
            type="primary"
            href={
              "/scenarios?strategic_prompt=" +
              encodeURIComponent(
                "The future of " + company?.business_brief?.company_name,
              )
            }
            target="_blank"
          >
            Brainstorm future scenarios and strategies
          </Button>
        )}
      </div>
      <br />
      <Row gutter={{ xs: 4, sm: 8, md: 16, lg: 24 }}>
        <Col className="gutter-row" span={6}>
          <div style={style}>
            <div className="company-dashboard-section">
              <h3>Business snapshot</h3>
              {company?.business_brief && (
                <div className="scenario">
                  <div
                    className="scenario-card-content"
                    style={{ height: "auto" }}
                  >
                    <div className="card-prop stackable">
                      <div className="card-prop-name">Revenue</div>
                      <div className="card-prop-value">
                        {company.business_brief.revenue}
                      </div>
                    </div>
                    <div className="card-prop stackable">
                      <div className="card-prop-name">Industry</div>
                      <div className="card-prop-value">
                        {company.business_brief.industry}
                      </div>
                    </div>
                    <div className="card-prop">
                      <div className="card-prop-name">Target customers</div>
                      <div className="card-prop-value">
                        {(company.business_brief.target_customers || []).join(
                          ", ",
                        )}
                      </div>
                    </div>
                    <div className="card-prop stackable">
                      <div className="card-prop-name">Key services</div>
                      <div className="card-prop-value">
                        {(company.business_brief.key_services || []).join(",")}
                      </div>
                    </div>
                    <div className="card-prop stackable">
                      <div className="card-prop-name">Upstream parties</div>
                      <div className="card-prop-value">
                        {company.business_brief.upstream_parties}
                      </div>
                    </div>
                    <div className="card-prop stackable">
                      <div className="card-prop-name">Downstream parties</div>
                      <div className="card-prop-value">
                        {company.business_brief.downstream_parties}
                      </div>
                    </div>
                    <div className="card-prop">
                      <div className="card-prop-name">Cost structure</div>
                      <div className="card-prop-value">
                        {(company.business_brief.cost_structure || []).join(
                          ", ",
                        )}
                      </div>
                    </div>
                    <div className="card-prop">
                      <div className="card-prop-name">Digital channels</div>
                      <div className="card-prop-value">
                        {(company.business_brief.digital_channels || []).join(
                          ", ",
                        )}
                      </div>
                    </div>
                    <div className="card-prop">
                      <div className="card-prop-name">Key acquisitions</div>
                      <div className="card-prop-value">
                        {(company.business_brief.key_acquisitions || []).join(
                          ", ",
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </Col>
        <Col className="gutter-row" span={10}>
          <div style={style}>
            <div className="company-dashboard-section small">
              <h3>Vision &amp; Strategic Priorities</h3>
              {company?.org_priorities && (
                <div className="scenario">
                  <div
                    className="scenario-card-content"
                    style={{ height: "auto" }}
                  >
                    <div className="card-prop stackable">
                      <div className="card-prop-name">Company vision</div>
                      <div className="card-prop-value">
                        {company.org_priorities.vision?.vision}
                      </div>
                      <div className="card-prop-value">
                        <a
                          href={(
                            company.org_priorities.vision?.references || []
                          ).join(", ")}
                        >
                          [source]
                        </a>
                      </div>
                    </div>
                    <div className="card-prop stackable">
                      <div className="card-prop-name">Strategic priorities</div>
                      <div className="card-prop-value">
                        {company.org_priorities.priorities?.priorities}
                      </div>
                      <div className="card-prop-value">
                        <a
                          href={(
                            company.org_priorities.priorities?.references || []
                          ).join(", ")}
                        >
                          [source]
                        </a>
                      </div>
                    </div>
                    <div className="card-prop stackable">
                      <div className="card-prop-name">KPIs</div>
                      <div className="card-prop-value">
                        {company.org_priorities.kpis?.kpis}
                      </div>
                      <div className="card-prop-value">
                        <a
                          href={(
                            company.org_priorities.kpis?.references || []
                          ).join(", ")}
                        >
                          [source]
                        </a>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
            <div className="company-dashboard-section small">
              <h3>Competitors</h3>
              {company?.competitors &&
                company?.competitors.map((df, i) => {
                  return (
                    <div key={i} className="scenario" title={df.name}>
                      <div
                        className="scenario-card-content"
                        style={{ height: "auto" }}
                      >
                        <div className="card-prop">
                          <div className="card-prop-name">{df.name}</div>
                        </div>
                        <div className="card-prop">
                          <div className="card-prop-name"></div>
                          <div className="card-prop-value">{df.rationale}</div>
                        </div>
                        <div className="card-prop">
                          <div className="card-prop-name">Key acquisitions</div>
                          <div className="card-prop-value">
                            {df.acquisitions}
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
            </div>
            <div className="company-dashboard-section small">
              <h3>Domain terms</h3>
              {company?.domain_terms &&
                company?.domain_terms.map((df, i) => {
                  return (
                    <div key={i} className="scenario">
                      <b>{df.term}</b>: {df.meaning}
                      <br />
                    </div>
                  );
                })}
            </div>
          </div>
        </Col>
        <Col className="gutter-row" span={7}>
          <div style={style}>
            <div className="company-dashboard-section">
              <h3>Domain Functions</h3>
              {company?.domain_functions &&
                company?.domain_functions.map((df, i) => {
                  return (
                    <div
                      key={i}
                      className="scenario"
                      title={"Function: " + df.name}
                    >
                      <div
                        className="scenario-card-content"
                        style={{ height: "auto" }}
                      >
                        <div className="card-prop">
                          <div className="card-prop-name">Function:</div>
                          <div className="card-prop-value">{df.name}</div>
                        </div>
                        <div className="card-prop">
                          <div className="card-prop-name">Description:</div>
                          <div className="card-prop-value">
                            {df.description}
                          </div>
                        </div>
                        <div className="card-prop">
                          <div className="card-prop-name">KPIs:</div>
                          <div className="card-prop-value">{df.kpi}</div>
                        </div>
                        <div className="card-prop">
                          <div className="card-prop-name">Use cases:</div>
                          <div className="card-prop-value">{df.use_cases}</div>
                        </div>
                        <div className="card-prop">
                          <div className="card-prop-name">Related systems:</div>
                          <div className="card-prop-value">
                            {df.related_systems}
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
            </div>
          </div>
        </Col>
      </Row>
    </div>
  );
};

export default CompanyDashboard;
