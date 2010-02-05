OBJ += main.o  configuration.o
TARGET = controller
LDFLAGS += -g -lPocoNet -lPocoXML -lboost_date_time
CXXFLAGS += -g

${TARGET}: ${OBJ}
	${LINK.cc} ${^} -o ${@}

%.PHONY:
clean:
	rm -f *.o ${TARGET}
