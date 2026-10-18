from parse_response import parse
cases=[("TARGET_A",False,False,("TARGET_A","OK")),(" STAFF\n",False,False,("STAFF","OK")),
("UNLABELABLE",False,False,("UNLABELABLE","OK")),("target_a",False,False,("UNLABELABLE","MALFORMED")),
("TARGET_A or TARGET_B",False,False,("UNLABELABLE","MALFORMED")),("TARGET_A.",False,False,("UNLABELABLE","MALFORMED")),
("Probably REFEREE",False,False,("UNLABELABLE","MALFORMED")),("",False,False,("UNLABELABLE","EMPTY")),
(None,False,False,("UNLABELABLE","EMPTY")),("x",True,False,("UNLABELABLE","REFUSAL_OR_BLOCK")),
(None,False,True,(None,"TRANSPORT_ERROR"))]
bad=[c for c in cases if parse(c[0],c[1],c[2])!=c[3]]
print("selftest_parse:", "FAIL" if bad else "OK", len(cases)); raise SystemExit(1 if bad else 0)
