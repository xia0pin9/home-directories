import os
import sys
import argparse
from androguard.core.bytecodes import apk
from androguard.core.bytecodes import dvm
from androguard.core.analysis import analysis

def process_dir(args):
    outputdir = args.outputdir
    dirname = args.inputdir
    if not os.path.exists(outputdir):
        os.mkdir(outputdir)
    else:
        confirm = raw_input("Output dir already exists, override? [y]/n")
        if confirm == "n":
            sys.exit(0)
    for root, dirs, files in os.walk(dirname):
        for filename in files:
            if not filename.endswith(".apk"):
                continue
            inputname = os.path.join(root, filename)
            targetname = os.path.join(outputdir, filename.replace(".apk", ".xml"))
            print(inputname)
            with open(targetname, "w") as f:
                a = apk.APK(inputname)
                f.write("<app name=\"{0}\">".format(a.package))
                d = dvm.DalvikVMFormat(a.get_dex())
                x = analysis.VMAnalysis(d)
                
                for method in d.get_methods():
                    try:
                        g = x.get_method(method)
                        if method.get_code() == None:
                            continue
                        #print method.get_class_name(), method.get_name(), method.get_descriptor()
                        
                        f.write("<m n=\"{0}\" s=\"{1}\">".format(method.get_name(), method.get_descriptor()))
                        for i in g.get_basic_blocks().get():
                            f.write("<bb>")
                            for ins in i.get_instructions():
                                o = ins.get_name()
                                istring = "<i o=\""+o+"\" "
                                variables = ins.get_output().split(", ")
                                if str(o).startswith("invoke"):
                                    if len(variables) > 5:
                                        istring += "vA=\"" + variables[-2] + "\" "
                                    istring += "vB=\"" + str(len(variables)) + "\" "
                                    istring += "vC=\"" + variables[-1] + "\" "
                                    insindex = ['v'+chr(68+j) for j in range(len(variables)-2)]
                                    insvalue = variables[:-2]
                                    istring += ' '.join('%s=\"%s\"' % t for t in zip(insindex, insvalue))
                                else:
                                    insindex = ['v'+chr(65+j) for j in range(len(variables))]                                    #
                                    istring += ' '.join('%s=\"%s\"' % t for t in zip(insindex, variables))
                                f.write(istring + " />")
                            f.write("</bb>")
                        f.write("</m>")
                    except:
                        raise
                        print "METHOD:", method.get_name(), method.get_descriptor()
                        # for i in method.get_instructions():
 #                            print i.get_name(), i.get_output()
                break


def main():
    parser = argparse.ArgumentParser(description="Convert android dalvik bytecode (dex) to xml format")
    parser.add_argument("-i", "--inputdir", default="samples", required=True, help="specify input directory")
    parser.add_argument("-o", "--outputdir", default="xml", help="specify xml output directory")
    args = parser.parse_args()
    process_dir(args)

if __name__ == "__main__":
    main()
