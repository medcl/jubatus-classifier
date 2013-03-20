#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
#based on git://github.com/jubatus/jubatus-tutorial-python.git
#modified by medcl,m@medcl.net
import sys,json
from jubatus.classifier import client
from jubatus.classifier import types

def parse_args():
    from optparse import OptionParser, OptionValueError
    p = OptionParser()
    #RPC 服务器地址
    p.add_option('-s', '--server_ip', action='store',
                 dest='server_ip', type='string', default='192.168.2.100')
    #RPC服务器端口
    p.add_option('-p', '--server_port', action='store',
                 dest='server_port', type='int', default='9198')
    #分类器名称
    p.add_option('-n', '--name', action='store',
                 dest='name', type='string', default='tutorial')
    #数据Field
    p.add_option('-k', '--key', action='store',
                 dest='key', type='string', default='message')
    #是否进行训练，如果不训练，则直接进入预测
    p.add_option('-t', '--train', action='store',
                 dest='train', type='string', default='true')
    #训练数据文件
    p.add_option('-x', '--train_file', action='store',
                 dest='train_file', type='string', default='train.dat')
    #测试数据文件
    p.add_option('-y', '--test_file', action='store',
                 dest='test_file', type='string', default='test.dat')
    #数据分隔符，2列，第一列为分类标识，第二列为数据
    p.add_option('-d', '--column_delimiter', action='store',
                 dest='column_delimiter', type='string', default=',')
    return p.parse_args()

def get_most_likely(estm):
    ans = None
    prob = None
    result = {}
    result[0] = ''
    result[1] = 0
    for res in estm:
        if prob == None or res.score > prob :
            ans = res.label
            prob = res.score
            result[0] = ans
            result[1] = prob
    return result



if __name__ == '__main__':
    options, remainder = parse_args()

    classifier = client.classifier(options.server_ip,options.server_port)

    pname = options.name

    print classifier.get_config(pname)
    print classifier.get_status(pname)
    splitter = re.compile(options.column_delimiter)

    trained_count=0
    #是否进行训练
    if(options.train=="true"):
        for line in open(options.train_file):
            array=splitter.split(line)
            if(len(array)==2):
                label, dat=array
                datum = types.datum(  [[options.key, dat]], [] )
                classifier.train(pname,[(label,datum)])
                trained_count=trained_count+1

        print classifier.get_status(pname)

        print classifier.save(pname, options.name)

    print classifier.load(pname, options.name)

    print classifier.get_config(pname)
    total=0.0
    hit=0.0
    for line in open(options.test_file):
        array=splitter.split(line)
        if(len(array)==2):
            label, dat=array
            datum = types.datum(  [[options.key, dat]], [] )
            ans = classifier.classify(pname,[(datum)])
            if ans != None:
                total=total+1
                estm = get_most_likely(ans[0])
                if (label == estm[0]):
                    result = "OK"
                    hit=hit+1
                else:
                    result = "NG"
                print result + "," + label + ", " + estm[0] + ", " + str(estm[1])

    print "trained:%d" % (trained_count)
    print "precision:%.2f" % (hit/total)
