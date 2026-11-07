"""Single entry point; all relative paths are rooted in --project-root."""
import argparse
import json
from pathlib import Path
from feedback_ai.config import Settings

def main(argv=None):
    parser=argparse.ArgumentParser(prog='feedback-ai')
    parser.add_argument('--project-root',required=True,type=Path)
    commands=parser.add_subparsers(dest='command',required=True)
    serve=commands.add_parser('serve');serve.add_argument('--port',type=int,default=8003);serve.add_argument('--host',default='127.0.0.1')
    bundle=commands.add_parser('bundle');bundle.add_argument('action',choices=['import']);bundle.add_argument('--source',type=Path,required=True)
    data=commands.add_parser('data');data.add_argument('action',choices=['import','acquire','validate','eda']);data.add_argument('--source',type=Path);data.add_argument('--output',type=Path)
    for name in ('train','evaluate'):
        cmd=commands.add_parser(name);cmd.add_argument('--task',choices=['sentiment','topic'],required=True);cmd.add_argument('--output',type=Path,required=True)
        if name=='evaluate':cmd.add_argument('--artifact',type=Path,required=True)
    exp=commands.add_parser('experiment');exp.add_argument('name',choices=['baseline','class_weights','word_char','augmentation','selective']);exp.add_argument('--config',type=Path,required=True);exp.add_argument('--output',type=Path,required=True)
    args=parser.parse_args(argv);settings=Settings.from_root(args.project_root)
    def path(value):return value.resolve() if value.is_absolute() else (settings.root/value).resolve()
    result=None
    if args.command=='serve':
        import uvicorn
        from feedback_ai.api.app import create_app
        uvicorn.run(create_app(settings),host=args.host,port=args.port)
    elif args.command=='bundle':
        from feedback_ai.inference.bundle import import_bundle
        result=str(import_bundle(path(args.source),settings.artifacts_dir/'serving'))
    elif args.command=='data':
        from feedback_ai.data import workflow
        raw=settings.data_dir/'raw'
        if args.action=='import':
            if args.source is None:parser.error('data import requires --source')
            result=workflow.import_data(path(args.source),raw)
        elif args.action=='acquire':result=workflow.acquire(raw)
        elif args.action=='validate':result=workflow.validate(raw,settings.data_dir/'manifest.json')
        else:
            if args.output is None:parser.error('data eda requires --output')
            result=workflow.eda(raw,path(args.output))
    elif args.command=='train':
        from feedback_ai.training.workflow import train
        result=train(args.task,settings.data_dir/'raw',path(args.output),settings.data_dir/'manifest.json')
    elif args.command=='evaluate':
        from feedback_ai.training.workflow import evaluate
        result=evaluate(args.task,path(args.artifact),settings.data_dir/'raw',path(args.output))
    else:
        from feedback_ai.training.experiments.runner import run_experiment
        config=json.loads(path(args.config).read_text(encoding='utf-8'))
        config['data_dir']=str(path(Path(config.get('data_dir','data/raw'))))
        for key in ('models','ct2_models','ct3_models'):
            if key in config:config[key]={task:str(path(Path(value))) for task,value in config[key].items()}
        result=run_experiment(args.name,config,path(args.output))
    if result is not None:print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
