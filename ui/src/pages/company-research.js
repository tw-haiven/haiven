// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { useSearchParams } from "next/navigation";
import React, { useState, useEffect } from "react";

import CompanyCanvas from "./_company_canvas";

export default function CompanyResearchPage() {
  const [researchConfig, setResearchConfig] = useState(null);

  const searchParams = useSearchParams();

  const availableResearchConfig = {
    company: {
      title: "Company overview",
      description:
        "Creates a 'quick glance' overview of a company, grounded with web search",
      key: "company",
      column1: [{ title: "Business Snapshot", property: "business_brief" }],
      column2: [
        { title: "Vision & Strategic Priorities", property: "org_priorities" },
        { title: "Competitors", property: "competitors" },
        { title: "Domain Terms", property: "domain_terms" },
      ],
      column3: [{ title: "Domain Functions", property: "domain_functions" }],
    },
    "ai-tool": {
      title: "Company overview - AI tools for the SDLC",
      description:
        "Creates a 'quick glance' overview of a company that builds AI tools for the SDLC, grounded with web search",
      key: "ai-tool",
      column1: [
        { title: "Business Snapshot", property: "business_brief" },
        { title: "Reception", property: "reception" },
      ],
      column2: [
        { title: "Vision & Strategic Priorities", property: "org_priorities" },
        { title: "Competitors", property: "competitors" },
        { title: "Did you know?", property: "other_tidbits" },
      ],
      column3: [
        {
          title: "Software Delivery Lifecycle Support",
          property: "software_lifecycle",
        },
        { title: "Key resources", property: "key_resources" },
      ],
    },
  };

  useEffect(() => {
    const configParam = searchParams.get("config");
    if (configParam && availableResearchConfig[configParam]) {
      setResearchConfig(availableResearchConfig[configParam]);
    } else {
      setResearchConfig(availableResearchConfig.company);
    }
  }, [searchParams]);

  return (
    <CompanyCanvas key={researchConfig.key} researchConfig={researchConfig} />
  );
}
