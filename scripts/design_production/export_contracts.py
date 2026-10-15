"""Reproducible schema export from the same models used by the SDK tools."""
import json
from . import contracts
from .policy import ROOT


def schemas():
    names=['DesignHookDecision','DesignTask','DesignResult','MainReviewDecision','ArtifactManifest','DesignQAReport','UnitContent','PresentationContract','EditorialContract','ReadInput','Empty']
    return {name:getattr(contracts,name).model_json_schema() for name in names}


if __name__=='__main__':
    path=ROOT/'.design-brain/runtime/design-production-contracts.json'
    path.write_text(json.dumps(schemas(),indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(path)
